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

engine = create_engine(RENDER_DB_URL)
SessionLocal = sessionmaker(bind=engine)

def fix_and_recalculate():
    db = SessionLocal()
    try:
        # 1. Remove the supply purchase that matches your starting balance
        print("Removing the 187,590 purchase record to fix double-counting...")
        db.execute(text("DELETE FROM purchasehist WHERE amount = 187590"))
        db.commit()

        # 2. Reset the ledger
        print("Resetting ledger table...")
        db.execute(text("TRUNCATE TABLE cash_ledger"))
        db.commit()

        # 3. Add Opening Balance
        starting_balance = 187590.0
        print(f"Adding Starting Balance of GH₵{starting_balance}...")
        
        # Using a slightly older date so it stays at the top
        opening_date = datetime.now(timezone.utc) - timedelta(days=365)
        
        db.execute(text("""
            INSERT INTO cash_ledger (ledger_id, transaction_type, amount, flow_type, balance_after, description, reference_id, date)
            VALUES (:id, 'INITIAL', :amount, 'IN', :balance, 'Initial Opening Balance', NULL, :date)
        """), {
            'id': uuid.uuid4(),
            'amount': starting_balance,
            'balance': starting_balance,
            'date': opening_date
        })

        # 4. Re-migrate existing transactions
        print("Fetching remaining transactions for migration...")
        
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
                'desc': f"Sale: {s[3]} (Qty: {s[4]})",
                'ref': s[0]
            })
            
        for p in purchases:
            all_transactions.append({
                'date': p[2],
                'amount': p[1],
                'type': 'PURCHASE',
                'flow': 'OUT',
                'desc': f"Purchase: {p[3]}",
                'ref': p[0]
            })
            
        # Sort by date
        all_transactions.sort(key=lambda x: x['date'])
        
        balance = starting_balance
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
        print(f"SUCCESS! The duplicate purchase has been removed.")
        print(f"New Final Account Balance: GH₵{balance}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_and_recalculate()
