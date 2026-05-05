import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add the parent directory to sys.path so we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

load_dotenv()

def migrate_to_float(db_url: str = None):
    """
    Connects to the database and updates specific columns from Integer to Float.
    """
    if not db_url:
        db_url = os.getenv("RENDER_POSTGRESS_DB_URL")
    
    if not db_url:
        print("Error: RENDER_POSTGRESS_DB_URL not found in environment variables.")
        return

    print(f"Connecting to database...")
    
    try:
        # Create engine
        engine = create_engine(db_url)
        
        # SQL commands to alter the tables
        # Using double precision which is the standard Float type in Postgres
        commands = [
            'ALTER TABLE products ALTER COLUMN "quantityInStock" TYPE DOUBLE PRECISION USING "quantityInStock"::DOUBLE PRECISION;',
            'ALTER TABLE products ALTER COLUMN "pricePerUnit" TYPE DOUBLE PRECISION USING "pricePerUnit"::DOUBLE PRECISION;',
            'ALTER TABLE sales ALTER COLUMN quantity_sold TYPE DOUBLE PRECISION USING quantity_sold::DOUBLE PRECISION;',
            'ALTER TABLE saleshist ALTER COLUMN quantity_sold TYPE DOUBLE PRECISION USING quantity_sold::DOUBLE PRECISION;'
        ]

        with engine.connect() as connection:
            print("Executing migrations...")
            for command in commands:
                print(f"Running: {command}")
                connection.execute(text(command))
            
            # Explicitly commit if not using autocommit mode (SQLAlchemy 2.0 style)
            connection.commit()
            
        print("\nSuccess: Database migration completed successfully.")
        print("Updated tables:")
        print("- products (quantityInStock, pricePerUnit)")
        print("- sales (quantity_sold)")
        print("- saleshist (quantity_sold)")

    except Exception as e:
        print(f"\nAn error occurred during migration: {e}")

if __name__ == "__main__":
    # If a URL is passed as a command line argument, use it
    url_arg = sys.argv[1] if len(sys.argv) > 1 else None
    migrate_to_float(url_arg)
