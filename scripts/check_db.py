import sqlite3
import os
from pathlib import Path

def check_db():
    db_path = Path(__file__).parent.parent / "data" / "database.db"
    print(f"Checking database at: {db_path}")
    
    if not db_path.exists():
        print(f"Database file does not exist at {db_path}")
        return
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("\nNo tables found in database!")
            return
            
        print("\nTables in database:")
        for table in tables:
            print(f"- {table[0]}")
            # Get count of rows
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  Count: {count}")
            
            # Get sample row if any exist
            cursor.execute(f"SELECT * FROM {table[0]} LIMIT 1")
            sample = cursor.fetchone()
            if sample:
                print(f"  Sample row: {sample}")
        
    except sqlite3.Error as e:
        print(f"Error accessing database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_db() 