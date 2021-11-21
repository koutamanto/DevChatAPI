import sqlite3, json

db_name = "groups.db"
group_conn = sqlite3.connect(db_name, check_same_thread=False)
group_cur = group_conn.cursor()

main_db_name = "main.db"
conn = sqlite3.connect(main_db_name, check_same_thread=False)
cur = conn.cursor()

while True:
    uid = input("uid:")
    cur.execute(f'SELECT name, email, icon_url FROM users WHERE id="{uid}"')
    name, email, icon_url = cur.fetchone()

    group_cur.execute(f'INSERT INTO g56db0108475d11e values("{uid}", "{name}", "{icon_url}", "{email}")')
    group_conn.commit()