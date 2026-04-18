import sqlite3
import re
from pathlib import Path

# Path to the database
DB_PATH = Path(__file__).parent / "db" / "db.sqlite"

def extract_material_name(sku: str) -> str:
    """
    Convert SKUs like:
    RM-C25-vitamin-d3-cholecalciferol-564712ba
    RM-C29-vitamin-d3-cholecalciferol-aedcde8b

    -> vitamin-d3-cholecalciferol
    """

    if not sku:
        return ""

    # remove prefix RM-Cxx-
    sku = re.sub(r"^RM-C\d+-", "", sku)

    # remove trailing hash
    sku = re.sub(r"-[a-f0-9]{6,}$", "", sku)

    return sku


def ensure_canonical_column():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(Product)")
    columns = [row[1] for row in cursor.fetchall()]

    if "canonical_material_name" not in columns:
        cursor.execute(
            "ALTER TABLE Product ADD COLUMN canonical_material_name TEXT"
        )
        conn.commit()

    conn.close()



def populate_canonical_material_name():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT Id, SKU
        FROM Product
        WHERE Type = 'raw-material'
        """
    )

    rows = cursor.fetchall()

    for product_id, sku in rows:
        canonical_name = extract_material_name(sku)
        cursor.execute(
            """
            UPDATE Product
            SET canonical_material_name = ?
            WHERE Id = ?
            """,
            (canonical_name, product_id),
        )

    conn.commit()
    conn.close()



def get_raw_materials():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT SKU, canonical_material_name
        FROM Product
        WHERE Type = 'raw-material'
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return rows


def group_materials():
    materials = get_raw_materials()

    grouped = {}

    for sku, canonical_name in materials:
        name = canonical_name or extract_material_name(sku)

        if name not in grouped:
            grouped[name] = []

        grouped[name].append(sku)

    return grouped


def main():
    ensure_canonical_column()
    populate_canonical_material_name()
    grouped = group_materials()

    print("canonical_material_name column ensured and populated.\n")

    for name, skus in grouped.items():
        print(f"\n{name}")
        for s in skus:
            print("   ", s)


if __name__ == "__main__":
    main()