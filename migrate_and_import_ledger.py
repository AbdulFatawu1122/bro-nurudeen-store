import os
import sys
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())
load_dotenv()

RENDER_DB_URL = os.getenv("RENDER_POSTGRESS_DB_URL")

if not RENDER_DB_URL:
    print("Error: RENDER_POSTGRESS_DB_URL not found in .env")
    exit(1)

# --- CONFIGURATION ---
STARTING_BALANCE = 187590.0
# ---------------------

engine = create_engine(RENDER_DB_URL)
SessionLocal = sessionmaker(bind=engine)

def migrate():
    # 1. Create the table if it doesn't exist
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS cash_ledger (
        ledger_id UUID PRIMARY KEY,
        transaction_type VARCHAR(50) NOT NULL,
        amount FLOAT NOT NULL,
        flow_type VARCHAR(10) NOT NULL,
        balance_after FLOAT NOT NULL,
        description TEXT,
        reference_id UUID,
        date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    with engine.connect() as conn:
        print("Ensuring cash_ledger table exists...")
        conn.execute(text(create_table_sql))
        conn.commit()

    db = SessionLocal()
    try:
        # 2. Reset the ledger (Empty the table to start fresh)
        print("Resetting ledger table...")
        db.execute(text("TRUNCATE TABLE cash_ledger"))
        db.commit()

        print(f"Adding Opening Balance of GH₵{STARTING_BALANCE}...")
        
        # Insert Initial Balance row
        # Using a slightly older date so it stays at the top
        opening_date = datetime.now(timezone.utc) - timedelta(days=365) 
        
        db.execute(text("""
            INSERT INTO cash_ledger (ledger_id, transaction_type, amount, flow_type, balance_after, description, reference_id, date)
            VALUES (:id, :type, :amount, :flow, :balance, :desc, :ref, :date)
        """), {
            'id': uuid.uuid4(),
            'type': 'INITIAL',
            'amount': STARTING_BALANCE,
            'flow': 'IN',
            'balance': STARTING_BALANCE,
            'desc': 'Initial Opening Balance (System Startup)',
            'ref': None,
            'date': opening_date
        })

        print("Fetching existing transactions for migration...")
        
        # Fetch Sales (Using double quotes for case-sensitive column names)
        sales = db.execute(text('SELECT "salehistId", amount, date, product_name, quantity_sold, customer_name FROM saleshist WHERE current_method = \'cash\'')).fetchall()
        
        # Fetch Purchases (Using double quotes for case-sensitive column names)
        purchases = db.execute(text('SELECT "purchaseHistId", amount, date, product_name, quantity, supplier_name FROM purchasehist WHERE current_method = \'cash\'')).fetchall()
        
        all_transactions = []
        
        for s in sales:
            all_transactions.append({
                'date': s[2],
                'amount': s[1],
                'type': 'SALE',
                'flow': 'IN',
                'desc': f"Imported Sale: {s[3]} (Qty: {s[4]}) - {s[5]}",
                'ref': s[0]
            })
            
        for p in purchases:
            all_transactions.append({
                'date': p[2],
                'amount': p[1],
                'type': 'PURCHASE',
                'flow': 'OUT',
                'desc': f"Imported Purchase: {p[3]} from {p[5]} (Qty: {p[4]})",
                'ref': p[0]
            })
            
        # Sort by date
        all_transactions.sort(key=lambda x: x['date'])
        
        balance = STARTING_BALANCE
        print(f"Migrating {len(all_transactions)} transactions...")
        
        for t in all_transactions:
            if t['flow'] == 'IN':
                balance += t['amount']
            else:
                balance -= t['amount']
                
            db.execute(text("""
                INSERT INTO cash_ledger (ledger_id, transaction_type, amount, flow_type, balance_after, description, reference_id, date)
                VALUES (:id, :type, :amount, :flow, :balance, :desc, :ref, :date)
            """), {
                'id': uuid.uuid4(),
                'type': t['type'],
                'amount': t['amount'],
                'flow': t['flow'],
                'balance': balance,
                'desc': t['desc'],
                'ref': t['ref'],
                'date': t['date']
            })
            
        db.commit()
        print(f"SUCCESS: Migrated {len(all_transactions)} transactions.")
        print(f"Final Account Balance: GH₵{balance}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
