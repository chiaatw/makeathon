

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / "db" / "db.sqlite"
MAP_TABLE = "canonical_material_supplier_map"


def get_connection():
    return sqlite3.connect(DB_PATH)


def ensure_mapping_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {MAP_TABLE} (
            canonical_material_name TEXT NOT NULL,
            supplier_id INTEGER NOT NULL,
            supplier_name TEXT NOT NULL,
            PRIMARY KEY (canonical_material_name, supplier_id),
            FOREIGN KEY (supplier_id) REFERENCES Supplier(Id)
        )
        """
    )

    conn.commit()
    conn.close()


def clear_mapping_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {MAP_TABLE}")
    conn.commit()
    conn.close()


def fetch_canonical_supplier_pairs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT DISTINCT
            p.canonical_material_name,
            s.Id,
            s.Name
        FROM Product p
        JOIN Supplier_Product sp ON sp.ProductId = p.Id
        JOIN Supplier s ON s.Id = sp.SupplierId
        WHERE p.Type = 'raw-material'
          AND p.canonical_material_name IS NOT NULL
          AND TRIM(p.canonical_material_name) != ''
          AND s.Name IS NOT NULL
          AND TRIM(s.Name) != ''
        ORDER BY p.canonical_material_name, s.Name
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return rows


def populate_mapping_table():
    pairs = fetch_canonical_supplier_pairs()

    conn = get_connection()
    cursor = conn.cursor()

    for canonical_material_name, supplier_id, supplier_name in pairs:
        cursor.execute(
            f"""
            INSERT OR REPLACE INTO {MAP_TABLE} (
                canonical_material_name,
                supplier_id,
                supplier_name
            )
            VALUES (?, ?, ?)
            """,
            (canonical_material_name, supplier_id, supplier_name),
        )

    conn.commit()
    conn.close()


def print_mapping_overview():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT canonical_material_name, supplier_name
        FROM {MAP_TABLE}
        ORDER BY canonical_material_name, supplier_name
        """
    )

    rows = cursor.fetchall()
    conn.close()

    grouped = {}
    for canonical_material_name, supplier_name in rows:
        if canonical_material_name not in grouped:
            grouped[canonical_material_name] = []
        grouped[canonical_material_name].append(supplier_name)

    for canonical_material_name, supplier_names in grouped.items():
        print(f"{canonical_material_name}")
        for supplier_name in supplier_names:
            print(f"   - {supplier_name}")
        print()


def main():
    print("Ensuring canonical_material_supplier_map exists...")
    ensure_mapping_table()

    print("Refreshing canonical material -> supplier mapping...")
    clear_mapping_table()
    populate_mapping_table()

    print("Done. Current mapping:\n")
    print_mapping_overview()


if __name__ == "__main__":
    main()