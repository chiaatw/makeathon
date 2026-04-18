import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / "db" / "db.sqlite"
SUPPLIER_COLUMN = "supplier_names"


def get_connection():
    return sqlite3.connect(DB_PATH)


def ensure_supplier_column():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(Product)")
    columns = [row[1] for row in cursor.fetchall()]

    if SUPPLIER_COLUMN not in columns:
        cursor.execute(f"ALTER TABLE Product ADD COLUMN {SUPPLIER_COLUMN} TEXT")
        conn.commit()

    conn.close()


def get_raw_materials():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT Id, SKU, canonical_material_name
        FROM Product
        WHERE Type = 'raw-material'
        ORDER BY SKU
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_supplier_for_product(product_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT s.Name
        FROM Supplier_Product sp
        JOIN Supplier s ON s.Id = sp.SupplierId
        WHERE sp.ProductId = ?
        ORDER BY sp.SupplierId
        LIMIT 1
        """,
        (product_id,),
    )

    row = cursor.fetchone()
    conn.close()

    return row[0] if row and row[0] else None


def update_supplier_names_column():
    conn = get_connection()
    cursor = conn.cursor()

    raw_materials = get_raw_materials()

    for product_id, sku, canonical_material_name in raw_materials:
        supplier_name = get_supplier_for_product(product_id)

        cursor.execute(
            f"""
            UPDATE Product
            SET {SUPPLIER_COLUMN} = ?
            WHERE Id = ?
            """,
            (supplier_name, product_id),
        )

    conn.commit()
    conn.close()


def print_supplier_overview():
    raw_materials = get_raw_materials()

    for _, sku, canonical_material_name in raw_materials:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT {SUPPLIER_COLUMN}
            FROM Product
            WHERE SKU = ?
            """,
            (sku,),
        )
        row = cursor.fetchone()
        conn.close()

        supplier_name = row[0] if row and row[0] else "none found"
        display_name = canonical_material_name or sku

        print(f"Raw material: {display_name}")
        print(f"SKU: {sku}")
        print(f"Supplier: {supplier_name}")
        print()


def main():
    print("Ensuring Product.supplier_names exists...")
    ensure_supplier_column()

    print("Populating supplier_names for raw materials...")
    update_supplier_names_column()

    print("Done. Current supplier overview:\n")
    print_supplier_overview()


if __name__ == "__main__":
    main()