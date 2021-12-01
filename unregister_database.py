import sqlite3, json

main_db_name = "main.db"
conn = sqlite3.connect(main_db_name, check_same_thread=False)
cur = conn.cursor()

uid = input("uid:")

cur.execute(f'DELETE FROM users WHERE id="{uid}"')