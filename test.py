import sqlite3

# Connect to SQLite database (creates database.db if it doesn’t exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Read and execute the schema.sql file
with open('schema.sql', 'r') as f:
    schema = f.read()
    cursor.executescript(schema)

# Commit changes and close connection
conn.commit()
conn.close()

print("SQLite database initialized successfully!")