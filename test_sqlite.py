import sqlite3
try:
    conn = sqlite3.connect('namonexus.db')
    print("Connection successful")
    c = conn.cursor()
    c.execute("CREATE TABLE test (id INTEGER)")
    print("Table created successfully")
    conn.commit()
    conn.close()
except Exception as e:
    print(e)