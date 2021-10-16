import sqlite3

db_name = "users.db"
conn = sqlite3.connect(db_name, check_same_thread=False)
cur = conn.cursor()
#cur.execute("drop table u7bd413bc2e1411e")
cur.execute('CREATE TABLE u7bd413bc2e1411e (id nvarchar[16], name STRING)')
conn.close()