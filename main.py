import uuid
from flask import Flask, jsonify, request
import sqlite3, json, requests
import smtplib, ssl
from email.mime.text import MIMEText
from datetime import datetime
app = Flask(__name__)

db_name = "main.db"
conn = sqlite3.connect(db_name, check_same_thread=False)
cur = conn.cursor()

user_db_name = "users.db"
user_conn = sqlite3.connect(user_db_name, check_same_thread=False)
user_cur = user_conn.cursor()
message_db_name = "messages.db"
message_conn = sqlite3.connect(message_db_name, check_same_thread=False)
message_cur = message_conn.cursor()

#cur.execute("CREATE TABLE user(uid nvarchar[16], name STRING)")
#cur.execute("CREATE TABLE gid(gid nvarchar[16], name STRING)")
#cur.execute("CREATE TABLE message(type STRING, body STRING, tid nvarchar[16], fid nvarchar[16])")
@app.route("/send_message", methods=["POST"])
def handle_message():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    from_uid = datas["from"]
    to = datas["to"]
    message = datas["message"]
    msg_type = message["type"]
    cur.execute(f'SELECT name FROM users WHERE id="{from_uid}"')
    name = cur.fetchone()[0]
    unix = datetime.now().timestamp()
    message_cur.execute(f'SELECT MAX(number) FROM {to}')
    last_number = message_cur.fetchone()[0] 
    print(last_number)
    if last_number == None:
        last_number = 0
    number = int(last_number) + 1
    if msg_type == "text":
        text = message["content"]
        message_cur.execute(f'INSERT INTO {to} values("{text}", "{from_uid}", "{name}", {unix}, {number})')
        
        message_conn.commit()
        return jsonify({"status":"success"})

@app.route("/delete_group", methods=["POST"])
def delete_group():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    msg_type = datas["type"]
    if msg_type == "delete_group":
        gid = datas["gid"]
        message_cur.execute(f'DROP TABLE {gid}')
        message_conn.commit()
        return jsonify({"status":"success"})

@app.route("/create_group", methods=["POST"])
def create_group():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    msg_type = datas["type"]
    if msg_type == "create_group":
        from_uid = datas["from"]
        name = datas["name"]
        uuid32 = uuid.uuid1().hex
        gid = "g" + uuid32[:15]
        print(gid)
        message_cur.execute(f'CREATE TABLE {gid} (content STRING, uid nvarchar[16], name STRING, unix REAL, number INTEGER)')
        cur.execute(f'INSERT INTO gid values("{gid}", "{name}")')
        conn.commit()
        return jsonify({"gid":gid})
@app.route("/register", methods=["POST"])
def register():
    #{
    #    "type": "sign_up",
    #    "user_name": "user_name",
    #    "mail_address": "user_mail_address",
    #    "pass_word": "user_pass_word"
    #}
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    type = datas["type"]
    if type == "first_sign_up":
        user_name = datas["user_name"]
        mail_address = datas["mail_address"]
        user_pass_word = datas["pass_word"]
        uuid32 = str(uuid.uuid1().hex)
        uid = "u" + uuid32[:15]
        cur.execute(f'SELECT id FROM WHERE id="{uid}"')
        is_exists_same_id = cur.fetchone()[0]
        if is_exists_same_id == None:
            pass
        elif is_exists_same_id != None:
            uuid32 = str(uuid.uuid1().hex)
            uid = "u" + uuid32[:15]
        otp = str(uuid.uuid1().int)[:4]
        cur.execute(f'SELECT email FROM users WHERE email="{mail_address}"')
        exists_mail_address = cur.fetchone()
        print(exists_mail_address)
        if exists_mail_address != None:                
            if mail_address not in exists_mail_address:
                cur.execute(f'INSERT INTO users values("{uid}", "{user_name}", "{mail_address}", "{user_pass_word}", {otp})')
                conn.commit()
            else:
                cur.execute(f'update users set lastotp={otp} where email="{mail_address}"')
                conn.commit()
        else:
            cur.execute(f'INSERT INTO users values("{uid}", "{user_name}", "{mail_address}", "{user_pass_word}", {otp})')
            conn.commit()
        # 以下にGmailの設定を書き込む★ --- (*1)
        gmail_account = "devchatotp@gmail.com"
        gmail_password = "kouta1014"
        # メールの送信先★ --- (*2)
        mail_to = mail_address

        # メールデータ(MIME)の作成 --- (*3)
        subject = "DevChatアカウント認証 ワンタイムパスワード"
        body = f"アプリに[{otp}]を入力してください。"
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["To"] = mail_to
        msg["From"] = gmail_account

        # Gmailに接続 --- (*4)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
            context=ssl.create_default_context())
        server.login(gmail_account, gmail_password)
        server.send_message(msg) # メールの送信
        print("ok.")
        return jsonify({"uid":uid})
    if type == "sign_up":
        uid = datas["uid"]
        otp = datas["otp"]
        uuid32 = str(uuid.uuid1().hex)
        cur.execute(f'UPDATE users set lastotp=0 where id="{uid}"')
        conn.commit()

        user_cur.execute(f'CREATE TABLE {uid} (id nvarchar[16], name STRING)')
        message_cur.execute(f'CREATE TABLE {uid} (type STRING, content STRING, tid nvarchar[16], fid nvarchar[16])')
        return jsonify({"uid":uid})

@app.route("/login", methods=["POST"])
def login():
    #{
    #    "type": "log_in",
    #    "mail_address": "user_mail_address",
    #    "pass_word": "user_pass_word"
    #}
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    type = datas["type"]
    if type == "log_in":
        mail_address = datas["mail_address"]
        user_pass_word = datas["pass_word"]
        cur.execute(f'SELECT password FROM users WHERE email="{mail_address}"')
        password = cur.fetchone()[0]
        if password == user_pass_word:
            cur.execute(f'SELECT id FROM users WHERE email="{mail_address}"')
            user_id = cur.fetchone()[0]
            user_cur.execute(f'SELECT id, name FROM {user_id}')
            friends_and_groups = user_cur.fetchall()
            groups = []
            friends = []
            for friend_or_group_uid, friend_or_group_name in friends_and_groups:
                if friend_or_group_uid[0] == "g":
                    groups.append({"group_name":friend_or_group_name, "group_uid":friend_or_group_uid})
                else:
                    friends.append({"friend_name":friend_or_group_name, "friend_uid":friend_or_group_uid})
            return jsonify({
                "friend": friends,
                "group": groups,
                "uid": user_id
            })
            #return jsonify({"status":"success", "uid":user_id})
        elif password != user_pass_word:
            return jsonify({"status":"failed", "reason":"password does not match"})

@app.route("/join_group", methods=["POST"])
def join_group():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    type = datas["type"]
    if type == "join_group":
        gid = datas["gid"]
        uid = datas["uid"]
        cur.execute(f'SELECT name FROM gid WHERE gid="{gid}"')
        name = cur.fetchone()[0]
        user_cur.execute(f'INSERT INTO {uid} values("{gid}", "{name}")')
        user_conn.commit()
        return jsonify({"status": "success"})

@app.route("/get_friend_list", methods=["POST"])
def get_friend_list():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    type = datas["type"]
    if type == "get_friend":
        uid = datas["uid"]

@app.route("/get_message", methods=["POST"])
def get_messages():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    type = datas["type"]
    if type == "get_message":
        gid = datas["gid"]
        message_cur.execute(f'SELECT content, uid, name, unix, number FROM {gid}')
        datas = message_cur.fetchall()
        send_datas = []
        count = 0
        for data in datas:
            if count < 100:
                count = count + 1
                content, uid, name, unix, number = data
                send_datas.append({"content":content, "uid":uid, "name":name, "unix":unix, "number":number})
            else:
                break
        return jsonify({"datas":send_datas})

@app.route("/forgot_password", methods=["POST"])
def forgot_password():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    type = datas["type"]
    if type == "first_forgot_password":
        otp = str(uuid.uuid1().int)[:4]
        mail_address = datas["mail_address"]
        cur.execute(f'SELECT id FROM users WHERE email="{mail_address}"')
        uid = cur.fetchone()[0]
        cur.execute(f'UPDATE users SET lastotp="{otp}"')
        conn.commit()
        # 以下にGmailの設定を書き込む★ --- (*1)
        gmail_account = "devchatotp@gmail.com"
        gmail_password = "kouta1014"
        # メールの送信先★ --- (*2)
        mail_to = mail_address

        # メールデータ(MIME)の作成 --- (*3)
        subject = "DevChatアカウント復元・パスワード変更 ワンタイムパスワード"
        body = f"アプリに[{otp}]を入力してください。"
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["To"] = mail_to
        msg["From"] = gmail_account

        # Gmailに接続 --- (*4)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
            context=ssl.create_default_context())
        server.login(gmail_account, gmail_password)
        server.send_message(msg) # メールの送信
        print("ok.")
        return jsonify({"uid":uid})
    if type == "forgot_password":
        otp = int(datas["otp"])
        uid = datas["uid"]
        cur.execute(f'SELECT lastotp FROM users WHERE id="{uid}"')
        lastotp = cur.fetchone()[0]
        
        if otp == lastotp:
            cur.execute(f'UPDATE users SET lastotp="0" WHERE id="{uid}"')
            conn.commit()
            return jsonify({"status":"success"})
        else:
            return jsonify({"status":"failed", "reason":"otp is not matched"})
    if type == "reset_password":
        uid = datas["uid"]
        new_password = datas["new_password"]
        cur.execute(f'SELECT lastotp FROM users WHERE id="{uid}"')
        lastotp = cur.fetchone()[0]
        if lastotp == 0:
            cur.execute(f'UPDATE users SET password="{new_password}" WHERE id="{uid}"')
            conn.commit()
            return jsonify({"status":"success"})
        else:
            return jsonify({"status":"failed", "reason":"otp was not matched before, or unexpected access from user"})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)