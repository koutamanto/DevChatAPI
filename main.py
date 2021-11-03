import base64
from io import BytesIO
import uuid
from PIL import Image
from flask import Flask, jsonify, request
import sqlite3, json, requests
from flask.templating import render_template
import smtplib, ssl
from email.mime.text import MIMEText
from datetime import datetime
from flask_swagger import swagger
from flask import send_file
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

app = Flask(__name__)

cred = credentials.Certificate("/root/DevChatAPI/devchat-82861-firebase-adminsdk-o28bl-df6393bfaf.json")
firebase_admin.initialize_app(cred)

# This registration token comes from the client FCM SDKs.
registration_token = 'YOUR_REGISTRATION_TOKEN'

db_name = "main.db"
conn = sqlite3.connect(db_name, check_same_thread=False)
cur = conn.cursor()

user_db_name = "users.db"
user_conn = sqlite3.connect(user_db_name, check_same_thread=False)
user_cur = user_conn.cursor()
message_db_name = "messages.db"
message_conn = sqlite3.connect(message_db_name, check_same_thread=False)
message_cur = message_conn.cursor()
group_db_name = "groups.db"
group_conn = sqlite3.connect(group_db_name, check_same_thread=False)
group_cur = group_conn.cursor()

#cur.execute("CREATE TABLE user(uid nvarchar[16], name STRING)")
#cur.execute("CREATE TABLE gid(gid nvarchar[16], name STRING)")
#cur.execute("CREATE TABLE message(type STRING, body STRING, tid nvarchar[16], fid nvarchar[16])")

#class db_controller:
#    def __init__(self, conn, cur, message_conn, message_cur, user_conn, user_cur):
#        self.conn, self.cur, self.message_conn, self.message_cur, self.user_conn, self.user_cur = conn, cur, message_conn, message_cur, user_conn, user_cur
#    def get_group_name(self, gid):
#        self.cur.execute(f'SELECT name FROM gid WHERE gid="{gid}"')
#        return self.cur.fetchone()[0]

#dbc = db_controller(conn, cur, message_conn, message_cur, user_conn, user_cur)

@app.route("/upload_icon", methods=["POST"])
def upload_icon():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    op_type = datas["type"]
    if op_type == "upload_icon":
        uid = datas["uid"]
        image = datas["content"]
        img = base64.b64decode(image) # base64に変換された画像データを元のバイナリデータに変換 # bytes
        img = BytesIO(img)
        image = Image.open(img)
        filename = datas["filename"]
        image.save("/root/DevChatAPI/images/" + filename)
        icon_url = "http://163.44.249.252/images/" + filename
        cur.execute(f'update users set icon_url="{icon_url}" WHERE id="{uid}"')
        conn.commit()
        return jsonify({
            "status":"success",
            "icon_url": icon_url
        })
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})
@app.route("/upload_group_icon", methods=["POST"])
def upload_group_icon():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    op_type = datas["type"]
    if op_type == "upload_group_icon":
        gid = datas["gid"]
        image = datas["content"]
        img = base64.b64decode(image) # base64に変換された画像データを元のバイナリデータに変換 # bytes
        img = BytesIO(img)
        image = Image.open(img)
        filename = datas["filename"]
        image.save("/root/DevChatAPI/images/" + filename)
        icon_url = "http://163.44.249.252/images/" + filename
        cur.execute(f'update gid set icon_url="{icon_url}" WHERE gid="{gid}"')
        conn.commit()
        return jsonify({
            "status":"success",
            "icon_url": icon_url
        })
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})
@app.route("/send_text_message", methods=["POST"])
def handle_text_message():
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
    cur.execute(f'SELECT name FROM gid WHERE gid="{to}"')
    group_name = cur.fetchone()[0]
    if msg_type == "text":
        text = message["content"]
        message_cur.execute(f'INSERT INTO {to} values("{text}", "{from_uid}", "{name}", {unix}, {number}, "{msg_type}")')
        
        message = messaging.Message(
            notification=messaging.Notification(
                title=group_name,
                body=f'[{name}:]{message}',
            ),
            topic=to,
        )

        # Send a message to the device corresponding to the provided
        # registration token.
        response = messaging.send(message)
        # Response is a message ID string.
        print('Successfully sent message:', response)

        message_conn.commit()
        return jsonify({"status":"success"})
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})

@app.route("/images/<string:filename>")
def send_uploaded_images(filename):
    return send_file("/root/DevChatAPI/images/" + filename, mimetype="image/gif")

@app.route("/add_friend", methods=["POST"])
def add_friend():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    op_type = datas["type"]
    if op_type == "add_friend":
        from_uid = datas["from_uid"]
        target_uid = datas["target_uid"]
        cur.execute(f'SELECT name FROM users WHERE id="{target_uid}"')
        target_name = cur.fetchone()[0]
        cur.execute(f'SELECT name FROM users WHERE id="{from_uid}"')
        from_name = cur.fetchone()[0]
        user_cur.execute(f'INSERT INTO {from_uid} values("{target_uid}", "{target_name}")')
        user_conn.commit()
        user_cur.execute(f'INSERT INTO {target_uid} values("{from_uid}", "{from_name}")')
        user_conn.commit()
        return jsonify(
            {
                "status": "success",
                "target_uid": target_uid
            }
        )
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})

@app.route("/send_image_message", methods=["POST"])
def handle_image_message():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    from_uid = datas["from"]
    to = datas["to"]
    message = datas["message"]
    msg_type = message["type"]
    filename = message["filename"]
    cur.execute(f'SELECT name FROM users WHERE id="{from_uid}"')
    name = cur.fetchone()[0]
    unix = datetime.now().timestamp()
    message_cur.execute(f'SELECT MAX(number) FROM {to}')
    last_number = message_cur.fetchone()[0]
    image = message["content"]
    img = base64.b64decode(image) # base64に変換された画像データを元のバイナリデータに変換 # bytes
    img = BytesIO(img)
    image = Image.open(img)
    image.save("/root/DevChatAPI/images/" + filename)
    print(last_number)
    if last_number == None:
        last_number = 0
    number = int(last_number) + 1
    if msg_type == "image":
        url = "http://163.44.249.252/images/" + filename
        message_cur.execute(f'INSERT INTO {to} values("{url}", "{from_uid}", "{name}", {unix}, {number}, "{msg_type}")')
        
        message_conn.commit()
        return jsonify({
            "status":"success", 
            "type":"image", 
            "url":"http://163.44.249.252/images/" + filename
        })
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})

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
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})

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
        message_cur.execute(f'CREATE TABLE {gid} (content STRING, uid nvarchar[16], name STRING, unix REAL, number INTEGER, type STRING)')
        cur.execute(f'INSERT INTO gid values("{gid}", "{name}", "")')
        conn.commit()
        group_cur.execute(f'CREATE TABLE {gid} (uid nvarchar[16], name STRING, icon STRING)')
        cur.execute(f'SELECT name FROM users WHERE id="{from_uid}"')
        user_name = cur.fetchone()[0]
        group_cur.execute(f'INSERT INTO {gid} values("{from_uid}", "{user_name}", "")')
        return jsonify({"status":"success","gid":gid})
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})

@app.route("/delete_folder", methods=["POST"])
def delete_folder():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    op_type = datas["type"]
    if op_type == "delete_folder":
        uid = datas["uid"]
        fid = datas["fid"]
        message_cur.execute(f'SELECT gid FROM {fid}')
        gids = message_cur.fetchall()
        print(gids)
        if gids == None:
            message_cur.execute(f'DROP TABLE {fid}')
            message_conn.commit()
            user_cur.execute(f'DELETE FROM {uid} WHERE id="{fid}"')
            user_conn.commit()
            return jsonify({"status":"success"})
        else:
            return jsonify({"status":"failed", "reason":"You can't delete folder contains groups"})
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})
@app.route("/make_folder", methods=["POST"])
def make_folder():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    op_type = datas["type"]
    if op_type == "make_folder":
        uid = datas["uid"]
        name = datas["name"]
        uuid32 = uuid.uuid1().hex
        fid = "f" + uuid32[:15]
        print(fid)
        user_cur.execute(f'INSERT INTO {uid} values("{fid}", "{name}")')
        user_conn.commit()
        message_cur.execute(f'CREATE TABLE {fid} (gid nvarchar[16], name STRING)')
        message_conn.commit()
        return jsonify(
            {
                "status":"success",
                "fid": fid
            }
        )
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})

@app.route("/put_into_folder", methods=["POST"])
def put_into_folder():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    op_type = datas["type"]
    if op_type == "put_into_folder":
        gid = datas["gid"]
        fid = datas["fid"]
        uid = datas["uid"]
        cur.execute(f'SELECT name FROM gid WHERE gid="{gid}"')
        group_name = cur.fetchone()[0]
        message_cur.execute(f'INSERT INTO {fid} values("{gid}", "{group_name}")')
        message_conn.commit()
        return jsonify(
            {
                "status":"success",
            })
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
        cur.execute(f'SELECT id FROM users WHERE id="{uid}"')
        is_exists_same_id = cur.fetchone()
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
            cur.execute(f'INSERT INTO users (id, name, email, password, lastotp) values("{uid}", "{user_name}", "{mail_address}", "{user_pass_word}", {otp})')
            conn.commit()
        # 以下にGmailの設定を書き込む★ --- (*1)
        gmail_account = "devchatotp@gmail.com"
        gmail_password = "kouta1014"
        # メールの送信先★ --- (*2)
        mail_to = mail_address

        # メールデータ(MIME)の作成 --- (*3)
        subject = "DevChatアカウント認証 ワンタイムパスワード"
        body = f"""アプリに[{otp}]を入力してください。
        
        ※心当たりのない場合は無視してください"""
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
        return jsonify({"status":"success","uid":uid})
    if type == "sign_up":
        uid = datas["uid"]
        otp = datas["otp"]
        uuid32 = str(uuid.uuid1().hex)
        cur.execute(f'UPDATE users set lastotp=0 where id="{uid}"')
        conn.commit()

        user_cur.execute(f'CREATE TABLE {uid} (id nvarchar[16], name STRING)')
        message_cur.execute(f'CREATE TABLE {uid} (type STRING, content STRING, tid nvarchar[16], fid nvarchar[16])')
        # 以下にGmailの設定を書き込む★ --- (*1)
        gmail_account = "devchatotp@gmail.com"
        gmail_password = "kouta1014"
        # メールの送信先★ --- (*2)
        
        cur.execute(f'SELECT email FROM users WHERE id="{uid}"')

        mail_to = cur.fetchone()[0]

        # メールデータ(MIME)の作成 --- (*3)
        subject = "DevChatアカウント認証 完了"
        body = f"""DevChatアカウントの認証が完了しました。
        アプリを開いてください。
        ※心当たりのない場合は無視してください"""
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
        return jsonify({"status":"success","uid":uid})
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})
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
            folders = []
            for friend_or_group_uid, friend_or_group_name in friends_and_groups:
                if friend_or_group_uid[0] == "g":
                    cur.execute(f'SELECT icon_url FROM gid WHERE gid="{friend_or_group_uid}"')
                    icon_url = cur.fetchone()
                    if icon_url != None:
                        icon_url_string = icon_url[0]
                        groups.append({"name":friend_or_group_name, "gid":friend_or_group_uid, "icon_url":icon_url_string})
                    elif icon_url == None:
                        icon_url_string = None
                        groups.append({"name":friend_or_group_name, "gid":friend_or_group_uid, "icon_url":icon_url_string})
                elif friend_or_group_uid[0] == "f":
                    print(friend_or_group_uid)
                    message_cur.execute(f'SELECT gid FROM {friend_or_group_uid}')
                    groups_inside_folder = message_cur.fetchall()
                    if groups_inside_folder == None:
                        folders.append({"name":friend_or_group_name, "fid":friend_or_group_uid, "groups":[]})
                    else:
                        folders.append({"name":friend_or_group_name, "fid":friend_or_group_uid, "groups":groups_inside_folder})
                else:
                    cur.execute(f'SELECT icon_url FROM users WHERE id="{friend_or_group_uid}"')
                    icon_url = cur.fetchone()
                    if icon_url != None:
                        icon_url_string = icon_url[0]
                        friends.append({"name":friend_or_group_name, "uid":friend_or_group_uid, "icon_url":icon_url_string})
                    if icon_url == None:
                        icon_url_string = None
                        friends.append({"name":friend_or_group_name, "uid":friend_or_group_uid, "icon_url":icon_url_string})
            return jsonify({
                "status":"success",
                "friend": friends,
                "group": groups,
                "folder": folders,
                "uid": user_id
            })
            #return jsonify({"status":"success", "uid":user_id})
        elif password != user_pass_word:
            return jsonify({"status":"failed", "reason":"password does not match"})
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})

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
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})
@app.route("/get_friend_list", methods=["POST"])
def get_friend_list():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    type = datas["type"]
    if type == "get_friend":
        uid = datas["uid"]
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})
@app.route("/unregister", methods=["POST"])
def delete_account():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    type = datas["type"]
    if type == "unregister":
        uid = datas["uid"]
        cur.execute(f'DELETE FROM users WHERE id="{uid}"')
        conn.commit()
        return jsonify({"status":"success"})
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})

@app.route("/leave_group", methods=["POST"])
def leave_group():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    op_type = datas["type"]
    if op_type == "leave_group":
        gid = datas["gid"]
        uid = datas["uid"]
        user_cur.execute(f'DELETE FROM {uid} WHERE id="{gid}"')
        return jsonify(
            {
                "status":"success"
            }
        )
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})
@app.route("/invite_into_group", methods=["POST"])
def invite_into_group():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    type = datas["type"]
    if type == "invite_into_group":
        target_uid = datas["target_uid"]
        to = datas["to"]
        uid = datas["uid"]
        cur.execute(f'SELECT name FROM gid WHERE gid="{to}"')
        group_name = cur.fetchone()[0]
        user_cur.execute(f'INSERT INTO {target_uid} values("{to}", "{group_name}")')
        return jsonify({"status":"success","gid":to})
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})
@app.route("/get_recent_message", methods=["POST"])
def get_recent_messages():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    type = datas["type"]
    if type == "get_recent_message":
        gid = datas["gid"]
        message_cur.execute(f'SELECT content, uid, name, unix, number FROM {gid}')
        datas = message_cur.fetchall()
        send_datas = []
        count = 0
        for data in datas:
            if count < 100:
                count = count + 1
                content, uid, name, unix, number, type = data
                send_datas.append({"content":content, "uid":uid, "name":name, "unix":unix, "number":number, "type":type})
            else:
                break
        return jsonify({"status":"success","datas":send_datas})
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})
@app.route("/get_all_message", methods=["POST"])
def get_all_messages():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    type = datas["type"]
    if type == "get_all_message":
        gid = datas["gid"]
        message_cur.execute(f'SELECT content, uid, name, unix, number, type FROM {gid}')
        datas = message_cur.fetchall()
        send_datas = []
        for data in datas:
            content, uid, name, unix, number, type = data
            send_datas.append({"content":content, "uid":uid, "name":name, "unix":unix, "number":number, "type":type})
        return jsonify({"status":"success","datas":send_datas})
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})
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
        return jsonify({"status":"success","uid":uid})
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
    else:
        return jsonify({"status":"failed", "reason":"invalid type"})
@app.route("/spec")
def spec():
    return jsonify(swagger(app))

@app.route("/test")
def test():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)