import sqlite3, json

db_name = "main.db"
conn = sqlite3.connect(db_name, check_same_thread=False)
cur = conn.cursor()
cur.execute(f'CREATE TABLE fcm(uid nvarchar[16], token STRING)')