import sqlite3

db_name = "groups.db"
conn = sqlite3.connect(db_name, check_same_thread=False)
cur = conn.cursor()