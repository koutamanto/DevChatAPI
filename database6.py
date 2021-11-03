import sqlite3, json

db_name = "main.db"
conn = sqlite3.connect(db_name, check_same_thread=False)
cur = conn.cursor()

cur.execute("DROP TABLE gid")
cur.execute('CREATE TABLE gid(gid nvarchar[16], name STRING, icon_url STRING)')
