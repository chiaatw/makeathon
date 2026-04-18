import sqlite3

# Read the SQL file
with open('queries.sql', 'r') as file:
    query = file.read()

# Connect and execute
with sqlite3.connect('db/db.sqlite') as conn:
    cursor = conn.cursor()
    cursor.execute(query)
    
    # Print the column headers
    columns = [desc[0] for desc in cursor.description]
    print(" | ".join(columns))
    print("-" * 50)
    
    # Print out each row
    for row in cursor.fetchall():
        print(" | ".join(map(str, row)))
