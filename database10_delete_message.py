import sqlite3, json

db_name = "messages.db"
conn = sqlite3.connect(db_name, check_same_thread=False)
cur = conn.cursor()

gid = "g56db0108475d11e"

cur.execute(f'DELETE FROM {gid} WHERE content="ブリ💩"')
conn.commit()