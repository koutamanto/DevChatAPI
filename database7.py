import sqlite3, json

db_name = "main.db"
conn = sqlite3.connect(db_name, check_same_thread=False)
cur = conn.cursor()
cur.execute(f'SELECT id FROM users')
uids = cur.fetchall()
for uid in uids:
    print(uid[0])
    cur.execute(f'SELECT icon_url FROM users WHERE id="{uid[0]}"')
    icon_url = cur.fetchone()[0]
    ssl_icon_url = icon_url.replace("https://163.44.249.252/", "https://devchat.jp/")
    cur.execute(f'UPDATE users SET icon_url="{ssl_icon_url}"')
    conn.commit()