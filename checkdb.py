import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM log LIMIT 5")
print(cursor.fetchall())
conn.close()