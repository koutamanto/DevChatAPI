import base64
from io import BytesIO
from os import name
import re
import uuid
from PIL import Image

from flask import Flask, jsonify, request
from flask_sslify import SSLify

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
from requests.api import get
from starlette.responses import JSONResponse
from werkzeug.utils import redirect
from login import loginV2
from get_messagesV2 import get_messagesV2
from get_group_name import getGroupName
from add_friend import add_friend

from fastapi import FastAPI, Form, Request
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import random
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class Item(BaseModel):
    language = "english"

sslify = SSLify(app)

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

@app.get("/", response_class=HTMLResponse)
async def root_page():
    return templates.TemplateResponse("index.html")

@app.post("/get_group_name")
async def get_group_name(request: Request):
    raw_datas = request.json()
    datas = json.loads(raw_datas)
    op_type = datas["type"]
    if op_type == "get_group_name":
        gid = datas["gid"]
        cur.execute(f'SELECT name FROM gid WHERE gid="{gid}"')
        group_name = cur.fetchone()[0]
        return JSONResponse({"status":"success", "gid":group_name})
@app.post("/upload_icon")
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
        icon_url = "http://devchat.jp/images/" + filename
        cur.execute(f'update users set icon_url="{icon_url}" WHERE id="{uid}"')
        conn.commit()
        return JSONResponse({
            "status":"success",
            "icon_url": icon_url
        })
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})
@app.get("/change_icon")
def change_icon_page():
    uid = request.cookies.get("uid")
    cur.execute(f'SELECT icon_url, name FROM users WHERE id="{uid}"')
    icon_url, name = cur.fetchone()
    return templates.TemplateResponse("change_icon/index.html", {"icon_url":icon_url, "name":name, "uid":uid})
@app.post("/upload_group_icon")
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
        icon_url = "http://devchat.jp/images/" + filename
        cur.execute(f'update gid set icon_url="{icon_url}" WHERE gid="{gid}"')
        conn.commit()
        return JSONResponse({
            "status":"success",
            "icon_url": icon_url
        })
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})
@app.post("/send_text_message")
def handle_text_message():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    from_uid = datas["sender"]
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
        group_cur.execute(f'SELECT email FROM {to}')
        email_addresses_of_users_inside_group = group_cur.fetchall()

        for mail_to in email_addresses_of_users_inside_group:
            gmail_account = "devchatotp@gmail.com"
            gmail_password = "kouta1014"
            # メールの送信先★ --- (*2)

            # メールデータ(MIME)の作成 --- (*3)
            subject = "DevChat メッセージが届きました"
            body = f"""[{name}:]{text}
            https://devchat.jp からログインして返信しよう！"""
            msg = MIMEText(body, "html")
            msg["Subject"] = subject
            msg["To"] = mail_to[0]
            msg["From"] = gmail_account

            # Gmailに接続 --- (*4)
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
                context=ssl.create_default_context())
            server.login(gmail_account, gmail_password)
            server.send_message(msg) # メールの送信
            print("ok.")
        #message = messaging.Message(
        #    notification=messaging.Notification(
        #        title=group_name,
        #        body=f'[{name}:]{message}',
        #    ),
        #    topic=to,
        #)
#
        ## Send a message to the device corresponding to the provided
        ## registration token.
        #response = messaging.send(message)
        ## Response is a message ID string.
        #print('Successfully sent message:', response)

        message_conn.commit()
        
        return JSONResponse({"status":"success"})
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})

@app.get("/images/<string:filename>")
def send_uploaded_images(filename):
    return FileResponse("/root/DevChatAPI/images/" + filename, mimetype="image/gif")

@app.get("/add/<string:target_uid>")
def add_page(target_uid):
    try:
        uid = request.cookies.get("uid")
        add_friend(uid, target_uid)
        return redirect("/home")
    except:
        return templates.TemplateResponse("login/add.html", {"target_uid":target_uid})

@app.post("/add_friend")
def add_friend_route():
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
        cur.execute(f'SELECT email FROM users WHERE id="{target_uid}"')
        mail_to = cur.fetchone()[0]
        cur.execute(f'SELECT name FROM users WHERE id="{from_uid}"')
        adder_name = cur.fetchone()[0]
        gmail_account = "devchatotp@gmail.com"
        gmail_password = "kouta1014"
        # メールの送信先★ --- (*2)

        # メールデータ(MIME)の作成 --- (*3)
        subject = "DevChat 友達追加されました"
        body = f"""{adder_name}があなたを友達追加しました
        https://devchat.jp からログインしてグループに招待しましょう！"""
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
        return JSONResponse(
            {
                "status": "success",
                "target_uid": target_uid
            }
        )
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})

@app.post("/send_image_message")
def handle_image_message():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    from_uid = datas["sender"]
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
        url = "http://devchat.jp/images/" + filename
        message_cur.execute(f'INSERT INTO {to} values("{url}", "{from_uid}", "{name}", {unix}, {number}, "{msg_type}")')
        
        message_conn.commit()
        return JSONResponse({
            "status":"success", 
            "type":"image", 
            "url":"http://devchat.jp/images/" + filename
        })
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})

@app.post("/delete_group")
def delete_group():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    msg_type = datas["type"]
    if msg_type == "delete_group":
        gid = datas["gid"]
        message_cur.execute(f'DROP TABLE {gid}')
        message_conn.commit()
        return JSONResponse({"status":"success"})
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})

@app.route("/create_group", methods=["POST", "GET"])
def create_group():
    if request.method == "POST":
        raw_datas = request.get_data()
        datas = json.loads(raw_datas)
        msg_type = datas["type"]
        if msg_type == "create_group":
            from_uid = datas["sender"]
            name = datas["name"]
            uuid32 = uuid.uuid1().hex
            gid = "g" + uuid32[:15]
            print(gid)
            message_cur.execute(f'CREATE TABLE {gid} (content STRING, uid nvarchar[16], name STRING, unix REAL, number INTEGER, type STRING)')
            cur.execute(f'INSERT INTO gid values("{gid}", "{name}", "http://devchat.jp/images/default_icon.png")')
            conn.commit()
            group_cur.execute(f'CREATE TABLE {gid} (uid nvarchar[16], name STRING, icon STRING, email STRING)')
            group_conn.commit()
            cur.execute(f'SELECT name FROM users WHERE id="{from_uid}"')
            user_name = cur.fetchone()[0]
            cur.execute(f'SELECT icon_url, email FROM users WHERE id="{from_uid}"')
            icon_url, email = cur.fetchone()
            group_cur.execute(f'INSERT INTO {gid} values("{from_uid}", "{user_name}", "{icon_url}", "{email}")')
            group_conn.commit()
            return JSONResponse({"status":"success","gid":gid})
        else:
            return JSONResponse({"status":"failed", "reason":"invalid type"})
    elif request.method == "GET":
        uid = request.cookies.get("uid")
        return templates.TemplateResponse("create_group/index.html", {"uid":uid})
@app.post("/delete_folder")
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
            return JSONResponse({"status":"success"})
        else:
            return JSONResponse({"status":"failed", "reason":"You can't delete folder contains groups"})
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})
@app.post("/make_folder")
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
        return JSONResponse(
            {
                "status":"success",
                "fid": fid
            }
        )
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})

@app.get("/profile/<string:uid>")
def profile_page(uid):
    cur.execute(f'SELECT name, icon_url FROM users WHERE id="{uid}"')
    name, icon_url = cur.fetchone()
    print(name, icon_url)
    return templates.TemplateResponse("profile/index.html", {"uid":uid, "name":name, "icon_url":icon_url})

@app.get("/invite/<string:target_uid>")
def invite_into_group_page(target_uid):
    uid = request.cookies.get("uid")
    user_cur.execute(f'SELECT id, name FROM {uid}')
    datas = user_cur.fetchall()
    gids = []
    names = []
    for gid, name in datas:
        if gid[0] == "g":
            gids.append(gid)
            names.append(name)
        else:
            pass
    print(datas)
    return templates.TemplateResponse("invite/index.html", {"uid":uid, "group_list":zip(gids, names), "target_uid":target_uid})

@app.post("/put_into_folder")
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
        return JSONResponse(
            {
                "status":"success",
            })
@app.post("/register")
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
                cur.execute(f'INSERT INTO users values("{uid}", "{user_name}", "{mail_address}", "{user_pass_word}", {otp}, "https://devchat.jp/images/default_icon.png")')
                conn.commit()
            else:
                cur.execute(f'update users set lastotp={otp} where email="{mail_address}"')
                conn.commit()
        else:
            cur.execute(f'INSERT INTO users (id, name, email, password, lastotp, icon_url) values("{uid}", "{user_name}", "{mail_address}", "{user_pass_word}", {otp}, "http://devchat.jp/images/default_icon.png")')
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
        return JSONResponse({"status":"success","uid":uid})
    if type == "sign_up":
        uid = datas["uid"]
        otp = datas["otp"]
        token = request.cookies.get("registration_token")
        cur.execute(f'INSERT INTO fcm values("{uid}", "{token}")')
        conn.commit()
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
        return JSONResponse({"status":"success","uid":uid})
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})
@app.route("/login", methods=["POST", "GET"])
def login():
    #{
    #    "type": "log_in",
    #    "mail_address": "user_mail_address",
    #    "pass_word": "user_pass_word"
    #}
    if request.method == "POST":
        raw_datas = request.get_data()
        print(raw_datas)
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
                return JSONResponse({
                    "status":"success",
                    "friend": friends,
                    "group": groups,
                    "folder": folders,
                    "uid": user_id
                })
                #return JSONResponse({"status":"success", "uid":user_id})
            elif password != user_pass_word:
                return JSONResponse({"status":"failed", "reason":"password does not match"})
        else:
            return JSONResponse({"status":"failed", "reason":"invalid type"})
    elif request.method == "GET":
        return templates.TemplateResponse("login/index.html")

@app.get("/favicon.ico")
def favicon():
    return FileResponse("images/favicon.ico")

@app.get("/firebase-messaging-sw.js")
def fcm_sw_js():
    return FileResponse("static/firebase-messaging-sw.js")

@app.get("/group/<string:gid>")
def group_talk(gid):
    uid = request.cookies.get("uid")
    datas = get_messagesV2(gid)
    group_name = getGroupName(gid)["gid"]
    return templates.TemplateResponse("group/index.html", {"datas":datas, "uid":uid, "gid":gid, "group_name":group_name})

@app.route("/otp_auth", methods=["GET"])
def otp_auth_page():
    uid = request.cookies.get("uid")
    return templates.TemplateResponse("register/otp.html", {"uid":uid})

@app.route("/register", methods=["GET"])
def register_page():
    return templates.TemplateResponse("register/index.html")

@app.route("/home", methods=["GET"])
def home_page():
    email = request.cookies.get("email")
    password = request.cookies.get("password")
    uid = request.cookies.get("uid")
    datas = loginV2(email, password)
    user_datas = datas["friend"]
    group_datas = datas["group"]
    folder_datas = datas["folder"]
    return templates.TemplateResponse("home/index.html", user_datas=user_datas, group_datas=group_datas, uid=uid)

@app.post("/join_group")
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
        return JSONResponse({"status": "success"})
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})
@app.post("/get_friend_list")
def get_friend_list():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    type = datas["type"]
    if type == "get_friend":
        uid = datas["uid"]
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})
@app.post("/unregister")
def delete_account():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    type = datas["type"]
    if type == "unregister":
        uid = datas["uid"]
        user_password = datas["password"]
        cur.execute(f'SELECT password FROM users WHERE id="{uid}"')
        password = cur.fetchone()[0]
        if user_password == password:
            cur.execute(f'DELETE FROM users WHERE id="{uid}"')
            conn.commit()
            user_cur.execute(f'DROP TABLE {uid}')
            return JSONResponse({"status":"success"})
        elif user_password != password:
            return JSONResponse({"status":"failed", "reason":"password does not match"})
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})

@app.post("/leave_group")
def leave_group():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    op_type = datas["type"]
    if op_type == "leave_group":
        gid = datas["gid"]
        uid = datas["uid"]
        user_cur.execute(f'DELETE FROM {uid} WHERE id="{gid}"')
        return JSONResponse(
            {
                "status":"success"
            }
        )
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})
@app.post("/invite_into_group")
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
        gmail_account = "devchatotp@gmail.com"
        gmail_password = "kouta1014"
        # メールの送信先★ --- (*2)
        cur.execute(f'SELECT email FROM users WHERE id="{target_uid}"')
        mail_to= cur.fetchone()[0]
        cur.execute(f'SELECT name FROM users WHERE id="{uid}"')
        inviter_name = cur.fetchone()[0]
        cur.execute(f'SELECT name, email FROM users WHERE id="{target_uid}"')
        target_name, email = cur.fetchone()
        cur.execute(f'SELECT icon_url FROM users WHERE id="{target_uid}"')
        target_icon_url = cur.fetchone()[0]
        # メールデータ(MIME)の作成 --- (*3)
        subject = "DevChat グループに招待されました"
        body = f"{inviter_name}があなたを{group_name}に招待しました\nhttps://devchat.jp からログインしてトークを始めましょう！"
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
        #user_registration_token = request.cookies.get("registration_token")
        #response = messaging.subscribe_to_topic(user_registration_token, to)
        ## See the TopicManagementResponse reference documentation
        ## for the contents of response.
        #print(response.success_count, 'tokens were subscribed successfully')
        user_cur.execute(f'INSERT INTO {target_uid} values("{to}", "{group_name}")')
        group_cur.execute(f'INSERT INTO {to} values("{target_uid}", "{target_name}", "{target_icon_url}", "{mail_to}")')
        user_conn.commit()
        group_conn.commit()
        return JSONResponse({"status":"success","gid":to})
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})
@app.post("/get_recent_message")
def get_recent_messages():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    type = datas["type"]
    if type == "get_recent_message":
        gid = datas["gid"]
        message_cur.execute(f'SELECT content, uid, name, unix, number, type FROM {gid}')
        datas = message_cur.fetchall()
        send_datas = []
        count = 0
        for data in datas:
            if count < 100:
                count = count + 1
                content, uid, name, unix, number, type = data
                cur.execute(f'SELECT icon_url FROM users WHERE id="{uid}"')
                fetched_icon_url = cur.fetchone()
                if  fetched_icon_url != None:
                    icon_url = fetched_icon_url[0]
                    send_datas.append({"content":content, "uid":uid, "name":name, "unix":unix, "number":number, "type":type, "icon_url":icon_url})
                elif fetched_icon_url == None:
                    pass
            else:
                break
        return JSONResponse({"status":"success","datas":send_datas})
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})
@app.post("/get_all_message")
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
        return JSONResponse({"status":"success","datas":send_datas})
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})
@app.post("/forgot_password")
def forgot_password():
    raw_datas = request.get_data()
    datas = json.loads(raw_datas)
    type = datas["type"]
    if type == "first_forgot_password":
        otp = str(uuid.uuid1().int)[:4]
        mail_address = datas["mail_address"]
        cur.execute(f'SELECT email FROM users WHERE email="{mail_address}"')
        exists_mail_address = cur.fetchone()
        print(exists_mail_address)
        if exists_mail_address != None:                
            if mail_address not in exists_mail_address:
                return JSONResponse({"status":"failed", "reason":"Email address is invalid or does not exists"})
            elif mail_address in exists_mail_address:
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
                return JSONResponse({"status":"success","uid":uid})
        else:
            return JSONResponse({"status":"failed", "reason": "Any email addresses found"})
    if type == "forgot_password":
        otp = int(datas["otp"])
        uid = datas["uid"]
        cur.execute(f'SELECT lastotp FROM users WHERE id="{uid}"')
        lastotp = cur.fetchone()[0]
        
        if otp == lastotp:
            cur.execute(f'UPDATE users SET lastotp="0" WHERE id="{uid}"')
            conn.commit()
            return JSONResponse({"status":"success"})
        else:
            return JSONResponse({"status":"failed", "reason":"otp is not matched"})
    if type == "reset_password":
        uid = datas["uid"]
        new_password = datas["new_password"]
        cur.execute(f'SELECT lastotp FROM users WHERE id="{uid}"')
        lastotp = cur.fetchone()[0]
        if lastotp == 0:
            cur.execute(f'UPDATE users SET password="{new_password}" WHERE id="{uid}"')
            conn.commit()
            return JSONResponse({"status":"success"})
        else:
            return JSONResponse({"status":"failed", "reason":"otp was not matched before, or unexpected access from user"})
    else:
        return JSONResponse({"status":"failed", "reason":"invalid type"})
#@app.get("/spec")
#def spec():
#    return JSONResponse(swagger(app))

@app.get("/test")
def test():
    return "ok"

if __name__ == "__main__":
    app.debug = True
    import ssl
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.load_cert_chain(
        'fullchain.pem', 'privkey.pem'
    )
    app.run(host="0.0.0.0", port=443, ssl_context=ssl_context)