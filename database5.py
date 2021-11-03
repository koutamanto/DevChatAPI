import sqlite3, json

db_name = "main.db"
conn = sqlite3.connect(db_name, check_same_thread=False)
cur = conn.cursor()

cur.execute("DROP TABLE users")
cur.execute("CREATE TABLE users(id nvarchar[16], name STRING, email STRING, password STRING, lastotp INTEGER, icon_url STRING)")