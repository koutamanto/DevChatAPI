import sqlite3

db_name = "messages.db"
conn = sqlite3.connect(db_name, check_same_thread=False)
cur = conn.cursor()
while True:
    table_name = input("table_name:")
    if table_name != "g664eda322e1311e":
        if table_name == "q":
            quit()
        else:
            cur.execute("drop table " + table_name)
    else:
        pass
#cur.execute('CREATE TABLE u7bd413bc2e1411e (id nvarchar[16], name STRING)')
conn.close()