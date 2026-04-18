import sqlite3

def explore_sqlite(db_path):
    print(f"Exploring database: {db_path}\n" + "-"*40)
    
    # Connect to the SQLite database
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
            return

        for (table_name,) in tables:
            print(f"\nTable: {table_name}")
            print("=" * (7 + len(table_name)))
            
            # Get column information
            cursor.execute(f"PRAGMA table_info('{table_name}');")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            print(f"Columns: {', '.join(col_names)}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM '{table_name}';")
            row_count = cursor.fetchone()[0]
            print(f"Row count: {row_count}")
            
            # Fetch sample data (up to 5 rows)
            if row_count > 0:
                print("Sample Data (up to 5 rows):")
                cursor.execute(f"SELECT * FROM '{table_name}' LIMIT 5;")
                for row in cursor.fetchall():
                    print(f"  {row}")
            print("-" * 40)

if __name__ == "__main__":
    explore_sqlite("db/db.sqlite")
