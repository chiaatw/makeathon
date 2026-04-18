import sqlite3
import sys

def search_products(search_term=""):
    db_path = "db/db.sqlite"
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Search for SKUs containing the search term
        query = """
            SELECT p.Id, p.SKU, c.Name as Company, p.Type
            FROM Product p
            LEFT JOIN Company c ON p.CompanyId = c.Id
            WHERE p.SKU LIKE ?
            LIMIT 20
        """
        
        cursor.execute(query, (f"%{search_term}%",))
        results = cursor.fetchall()
        
        if not results:
            print(f"No products found matching '{search_term}'")
            return
            
        print(f"\n--- Search Results for '{search_term}' ---")
        print(f"{'ID':<5} | {'SKU':<45} | {'Company':<25} | {'Type'}")
        print("-" * 100)
        for row in results:
            print(f"{row[0]:<5} | {row[1]:<45} | {str(row[2]):<25} | {row[3]}")

if __name__ == "__main__":
    term = sys.argv[1] if len(sys.argv) > 1 else ""
    search_products(term)
