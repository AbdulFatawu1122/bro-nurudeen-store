import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add current directory to path to find .env if needed
sys.path.append(os.getcwd())
load_dotenv()

RENDER_DB_URL = os.getenv("RENDER_POSTGRESS_DB_URL")

if not RENDER_DB_URL:
    print("Error: RENDER_POSTGRESS_DB_URL not found in .env")
    exit(1)

# Create engine
# For Postgres on Render, sometimes you need the external URL if running from outside
# but we will try the one provided first.
engine = create_engine(RENDER_DB_URL)

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

print(f"Connecting to: {RENDER_DB_URL.split('@')[-1]}") # Print host only for security

try:
    with engine.connect() as conn:
        print("Connected successfully. Creating table...")
        conn.execute(text(create_table_sql))
        conn.commit()
    print("SUCCESS: cash_ledger table is ready!")
except Exception as e:
    print(f"FAILED: {e}")
