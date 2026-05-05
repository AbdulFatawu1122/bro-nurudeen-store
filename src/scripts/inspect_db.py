import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add the parent directory to sys.path so we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

load_dotenv()

def inspect_tables(db_url: str = None):
    """
    Connects to the database and shows the data types of columns in specified tables.
    """
    if not db_url:
        db_url = os.getenv("RENDER_POSTGRESS_DB_URL")
    
    if not db_url:
        print("Error: RENDER_POSTGRESS_DB_URL not found in environment variables.")
        return

    print(f"Connecting to database to inspect columns...")
    
    try:
        engine = create_engine(db_url)
        tables_to_inspect = ['products', 'sales', 'saleshist']
        
        with engine.connect() as connection:
            for table in tables_to_inspect:
                print(f"\n--- Table: {table} ---")
                # Query information_schema for column details
                query = text("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = :table 
                    ORDER BY ordinal_position;
                """)
                
                result = connection.execute(query, {"table": table})
                
                print(f"{'Column Name':<25} | {'Data Type':<20} | {'Nullable'}")
                print("-" * 60)
                for row in result:
                    col_name, data_type, nullable = row
                    print(f"{col_name:<25} | {data_type:<20} | {nullable}")

        print("\nInspection complete.")

    except Exception as e:
        print(f"\nAn error occurred during inspection: {e}")

if __name__ == "__main__":
    url_arg = sys.argv[1] if len(sys.argv) > 1 else None
    inspect_tables(url_arg)
