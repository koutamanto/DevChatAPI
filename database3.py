import sqlite3

db_name = "users.db"
conn = sqlite3.connect(db_name, check_same_thread=False)
cur = conn.cursor()
cur.execute("DELETE FROM u7bd413bc2e1411e WHERE id='f02d25536377011e'")
conn.commit()