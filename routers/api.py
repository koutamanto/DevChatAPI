# routers/api.py
from datetime import datetime
from io import BytesIO
import json, sqlite3, base64, smtplib, ssl, uuid, sys, demoji
from email.mime.text import MIMEText
from fastapi import APIRouter
from fastapi.params import Cookie
from fastapi.responses import UJSONResponse
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import request_response
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from starlette.templating import Jinja2Templates
from werkzeug.wrappers import response
from models.model import *
from PIL import Image
sys.path.append("../")
from add_friend import add_friend
templates = Jinja2Templates(directory="templates")

router = APIRouter(default_response_class=UJSONResponse)
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

router.mount("/static", StaticFiles(directory="static"), name="static")
@router.post("/get_group_name", response_class=JSONResponse)
async def get_group_name(raw: getGroupName):
    datas = jsonable_encoder(raw)
    op_type = datas["type"]
    if op_type == "get_group_name":
        gid = datas["gid"]
        cur.execute(f'SELECT name FROM gid WHERE gid="{gid}"')
        group_name = cur.fetchone()[0]
        return {"status":"success", "gid":group_name}
    else:
        return {"status":"failed", "reason":"invalid type"}

@router.post("/upload_icon", response_class=UJSONResponse)
def upload_icon(raw: uploadIcon):
    datas = jsonable_encoder(raw)
    op_type = datas["type"]
    if op_type == "upload_icon":
        uid = datas["uid"]
        image = datas["content"]
        img = base64.b64decode(image) # base64に変換された画像データを元のバイナリデータに変換 # bytes
        img = BytesIO(img)
        image = Image.open(img)
        center_x = int(image.width / 2)
        center_y = int(image.height / 2)
        if image.width < image.height:
            shorter_one = image.width
        elif image.width > image.height:
            shorter_one = image.height
        elif image.width == image.height:
            shorter_one = image.height
        new_size = shorter_one
        img_crop = image.crop((center_x - new_size / 2, center_y - new_size / 2, center_x + new_size / 2, center_y + new_size / 2))
        filename = datas["filename"]
        img_crop.save("/root/DevChatAPI/images/" + filename)
        icon_url = "http://devchat.jp/images/" + filename
        cur.execute(f'update users set icon_url="{icon_url}" WHERE id="{uid}"')
        conn.commit()
        return {
            "status":"success",
            "icon_url": icon_url,
            "uid": uid
        }
    else:
        return {"status":"failed", "reason":"invalid type"}

@router.post("/upload_group_icon", response_class=UJSONResponse)
def upload_group_icon(raw: uploadGroupIcon):
    datas = jsonable_encoder(raw)
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
        return {
            "status":"success",
            "icon_url": icon_url
        }
    else:
        return {"status":"failed", "reason":"invalid type"}

@router.post("/send_html_message_with_url", response_model=sendHTMLMessageResponse)
def send_html_message_with_url(raw: sendHTMLMessage):
    datas = jsonable_encoder(raw)
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
    if msg_type == "html_url":
        url = message["content"]
        message_cur.execute(f'INSERT INTO {to} values("{url}", "{from_uid}", "{name}", {unix}, {number}, "{msg_type}")')
        group_cur.execute(f'SELECT email FROM {to}')
        email_addresses_of_users_inside_group = group_cur.fetchall()

        for mail_to in email_addresses_of_users_inside_group:
            gmail_account = "devchatotp@gmail.com"
            gmail_password = "kouta1014"
            # メールの送信先★ --- (*2)

            # メールデータ(MIME)の作成 --- (*3)
            subject = "DevChat HTMLメッセージが届きました"
            body = f"""見てみよう！
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
            print("ok.", mail_to[0])
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
        
        return {"status":"success", "url": url}
    else:
        return {"status":"failed", "reason":"invalid type"}    

@router.post("/send_html_message", response_model=sendHTMLMessageResponse)
def send_html_message(raw: sendHTMLMessage):
    datas = jsonable_encoder(raw)
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
    if msg_type == "html":
        content = message["content"]
        with open(f"templates/html_messages/{to}_{str(number)}.html", "w") as f:
            f.write(content)
        message_cur.execute(f'INSERT INTO {to} values("https://devchat.jp/html_messages/{to}_{str(number)}.html", "{from_uid}", "{name}", {unix}, {number}, "{msg_type}")')
        group_cur.execute(f'SELECT email FROM {to}')
        email_addresses_of_users_inside_group = group_cur.fetchall()

        for mail_to in email_addresses_of_users_inside_group:
            gmail_account = "devchatotp@gmail.com"
            gmail_password = "kouta1014"
            # メールの送信先★ --- (*2)

            # メールデータ(MIME)の作成 --- (*3)
            subject = "DevChat HTMLメッセージが届きました"
            body = f"""見てみよう！
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
            print("ok.", mail_to[0])
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
        
        return {"status":"success", "url":f"https://devchat.jp/html_messages/{to}_{str(number)}.html"}
    else:
        return {"status":"failed", "reason":"invalid type"}

@router.post("/send_text_message", response_class=UJSONResponse, response_model=statusSuccess)
def send_text_message(raw: sendTextMessage):
    datas = jsonable_encoder(raw)
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
        text = demoji.replace(string=text, repl="")
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
            print("ok.", mail_to[0])
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
        
        return {"status":"success"}
    else:
        return {"status":"failed", "reason":"invalid type"}

@router.post("/send_image_message", response_class=UJSONResponse, response_model=sendImageMessageResponse)
def handle_image_message(raw: sendImageMessage):
    datas = jsonable_encoder(raw)
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
        return {
            "status":"success", 
            "type":"image", 
            "url":"http://devchat.jp/images/" + filename
        }
    else:
        return {"status":"failed", "reason":"invalid type"}

@router.post("/create_group", response_class=UJSONResponse, response_model=createGroupResponse)
def create_group(raw: createGroup):
    datas = jsonable_encoder(raw)
    msg_type = datas["type"]
    if msg_type == "create_group":
        from_uid = datas["uid"]
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
        unix = datetime.now().timestamp()
        message_cur.execute(f'SELECT MAX(number) FROM {gid}')
        last_number = message_cur.fetchone()[0] 
        print(last_number)
        if last_number == None:
            last_number = 0
        number = int(last_number) + 1
        message_cur.execute(f'INSERT INTO {gid} values("{user_name}がグループを作成しました", "ub56e2352490711e", "DevChatログ", {unix}, {number}, "log")')
        message_conn.commit()
        return {"status":"success","gid":gid}
    else:
        return {"status":"failed", "reason":"invalid type"}

@router.post("/make_folder", response_class=UJSONResponse, response_model=makeFolderResponse)
def make_folder(raw: makeFolder):
    datas = jsonable_encoder(raw)
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
        return {
                "status":"success",
                "fid": fid
            }
    else:
        return {"status":"failed", "reason":"invalid type"}

@router.post("/put_into_folder", response_class=UJSONResponse, response_model=putIntoFolderResponse)
def put_into_folder(raw: deleteFolder):
    datas = jsonable_encoder(raw)
    op_type = datas["type"]
    if op_type == "put_into_folder":
        gid = datas["gid"]
        fid = datas["fid"]
        uid = datas["uid"]
        cur.execute(f'SELECT name FROM gid WHERE gid="{gid}"')
        group_name = cur.fetchone()[0]
        message_cur.execute(f'INSERT INTO {fid} values("{gid}", "{group_name}")')
        message_conn.commit()
        return {
                "status":"success",
            }
    else:
        return {"status":"failed", "reason":"invalid type"}

@router.post("/first_sign_up", response_class=UJSONResponse, response_model=firstSignUpResponse)
def first_sign_up(raw: firstSignUp):
    datas = jsonable_encoder(raw)
    op_type = datas["type"]
    if op_type == "first_sign_up":
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
        return {"status":"success","uid":uid}
    else:
        return {"status":"failed", "reason":"invalid type"}

@router.post("/sign_up", response_model=signUpResponse)
def sign_up(raw: signUp, token: str = Cookie(None)):
    datas = jsonable_encoder(raw)
    op_type = datas["type"]
    if op_type == "sign_up":
        uid = datas["uid"]
        otp = datas["otp"]
        cur.execute(f'INSERT INTO fcm values("{uid}", "{token}")')
        conn.commit()
        uuid32 = str(uuid.uuid1().hex)
        cur.execute(f'UPDATE users set lastotp=0 where id="{uid}"')
        conn.commit()
        try:        
            user_cur.execute(f"CREATE TABLE {uid} (id nvarchar[16], name STRING)")
        except Exception as e:
            print(e)
            pass
        try:
            message_cur.execute(
                f"CREATE TABLE {uid} (type STRING, content STRING, tid nvarchar[16], fid nvarchar[16])"
            )
        except Exception as e:
            print(e)
            pass
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
        server = smtplib.SMTP_SSL(
            "smtp.gmail.com", 465, context=ssl.create_default_context()
        )
        server.login(gmail_account, gmail_password)
        server.send_message(msg)  # メールの送信
        cur.execute(f'SELECT name FROM gid WHERE gid="g56db0108475d11e"')
        name = cur.fetchone()[0]
        user_cur.execute(f'INSERT INTO {uid} values("g56db0108475d11e", "{name}")')
        user_conn.commit()
        group_cur.execute(f'INSERT INTO g56db0108475d11e values("{uid}", "{name}", "https://devchat.jp/images/{uid}.png", "{mail_to}")')
        group_conn.commit()
        add_friend(uid, "u4a6d8b5e42ce11e")
        print("ok.")
        return {"status": "success", "uid": uid}
    else:
        return {"status": "failed", "reason": "invalid type"}
@router.post("/login", response_model=loginResponse)
async def login(raw: loginRequest):
    datas = jsonable_encoder(raw)
    op_type = datas["type"]
    if op_type == "log_in":
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
                    #print(friend_or_group_uid)
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
            return {
                "status":"success",
                "friend": friends,
                "group": groups,
                "folder": folders,
                "uid": user_id
            }
            #return {"status":"success", "uid":user_id}
        elif password != user_pass_word:
            return {"status":"failed", "reason":"password does not match"}
    else:
        return {"status":"failed", "reason":"invalid type"}

@router.post("/add_friend", response_model=addFriendResponse)
def add_friend_api(raw: addFriend):
    datas = jsonable_encoder(raw)
    op_type = datas["type"]
    if op_type == "add_friend":
        from_uid = datas["from_uid"]
        target_uid = datas["target_uid"]
        cur.execute(f'SELECT name FROM users WHERE id="{target_uid}"')
        target_name = cur.fetchone()[0]
        cur.execute(f'SELECT name FROM users WHERE id="{from_uid}"')
        from_name = cur.fetchone()[0]
        user_cur.execute(f'SELECT id FROM {from_uid}')
        from_user_added_uids = user_cur.fetchall()
        if target_uid not in from_user_added_uids:
            user_cur.execute(
                f'INSERT INTO {from_uid} values("{target_uid}", "{target_name}")'
            )
            user_conn.commit()
        else:
            return {"status":"failed", "reason":"you can't add user already added before."}
        user_cur.execute(f'SELECT id FROM {target_uid}')
        target_user_added_uids = user_cur.fetchall()
        if from_uid not in target_user_added_uids:
            user_cur.execute(
                f'INSERT INTO {target_uid} values("{from_uid}", "{from_name}")'
            )
            user_conn.commit()
        else:
            return {"status":"failed", "reason":"you can't add user already added before."}
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
        server = smtplib.SMTP_SSL(
            "smtp.gmail.com", 465, context=ssl.create_default_context()
        )
        server.login(gmail_account, gmail_password)
        server.send_message(msg)  # メールの送信
        print("ok.")
        return {"status": "success", "target_uid": target_uid}
    else:
        return {"status": "failed", "reason": "invalid type"}

@router.post("/join_group", response_model=statusSuccess)
def join_group(raw: joinGroup):
    datas = jsonable_encoder(raw)
    type = datas["type"]
    if type == "join_group":
        gid = datas["gid"]
        uid = datas["uid"]
        cur.execute(f'SELECT name FROM gid WHERE gid="{gid}"')
        name = cur.fetchone()[0]
        user_cur.execute(f'INSERT INTO {uid} values("{gid}", "{name}")')
        user_conn.commit()
        return {"status": "success", "gid":gid}
    else:
        return {"status":"failed", "reason":"invalid type"}

@router.post("/unregister", response_model=statusSuccess)
def delete_account(raw: unregister):
    datas = jsonable_encoder(raw)
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
            return {"status":"success"}
        elif user_password != password:
            return {"status":"failed", "reason":"password does not match"}
    else:
        return {"status":"failed", "reason":"invalid type"}

@router.post("/leave_group", response_model=statusSuccess)
def leave_group(raw: leaveGroup):
    datas = jsonable_encoder(raw)
    op_type = datas["type"]
    if op_type == "leave_group":
        gid = datas["gid"]
        uid = datas["uid"]
        unix = datetime.now().timestamp()
        message_cur.execute(f'SELECT MAX(number) FROM {gid}')
        last_number = message_cur.fetchone()[0] 
        print(last_number)
        if last_number == None:
            last_number = 0
        number = int(last_number) + 1
        cur.execute(f'SELECT name FROM users WHERE id="{uid}"')
        user_name = cur.fetchone()[0]
        message_cur.execute(f'INSERT INTO {gid} values("{user_name}がグループを抜けました", "ub56e2352490711e", "DevChatログ", {unix}, {number}, "log")')
        message_conn.commit()
        user_cur.execute(f'DELETE FROM {uid} WHERE id="{gid}"')
        return {
                "status":"success"
            }
    else:
        return {"status":"failed", "reason":"invalid type"}

@router.post("/invite_into_group", response_model=inviteIntoGroupResponse)
def invite_into_group(raw: inviteIntoGroup):
    datas = jsonable_encoder(raw)
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
        unix = datetime.now().timestamp()
        message_cur.execute(f'SELECT MAX(number) FROM {to}')
        last_number = message_cur.fetchone()[0] 
        print(last_number)
        if last_number == None:
            last_number = 0
        number = int(last_number) + 1
        message_cur.execute(f'INSERT INTO {to} values("{inviter_name}が{target_name}を招待しました", "ub56e2352490711e", "DevChatログ", {unix}, {number}, "log")')
        message_conn.commit()
        user_cur.execute(f'SELECT id FROM {target_uid}')
        user_cur.execute(f'INSERT INTO {target_uid} values("{to}", "{group_name}")')
        group_cur.execute(f'INSERT INTO {to} values("{target_uid}", "{target_name}", "{target_icon_url}", "{mail_to}")')
        user_conn.commit()
        group_conn.commit()
        return {"status":"success","gid":to}
    else:
        return {"status":"failed", "reason":"invalid type"}

@router.post("/get_recent_message", response_model=getRecentMessageResponse)
async def get_recent_message(raw: getRecentMessage):
    datas = jsonable_encoder(raw)
    type = datas["type"]
    if type == "get_recent_message":
        gid = datas["gid"]
        message_cur.execute(f"SELECT content, uid, name, unix, number, type FROM {gid}")
        datas = message_cur.fetchall()
        send_datas = []
        count = 0
        for data in datas:
            if count < 100:
                count = count + 1
                content, uid, name, unix, number, type = data
                cur.execute(f'SELECT icon_url FROM users WHERE id="{uid}"')
                fetched_icon_url = cur.fetchone()
                if fetched_icon_url != None:
                    icon_url = fetched_icon_url[0]
                    send_datas.append(
                        {
                            "content": content,
                            "uid": uid,
                            "name": name,
                            "unix": unix,
                            "number": number,
                            "type": type,
                            "icon_url": icon_url,
                        }
                    )
                elif fetched_icon_url == None:
                    pass
            else:
                break
        return {"status": "success", "datas": send_datas}
    else:
        return {"status": "failed", "reason": "invalid type"}

@router.post("/get_all_message", response_model=getAllMessagesResponse)
def get_all_messages(raw: getAllMessages):
    datas = jsonable_encoder(raw)
    type = datas["type"]
    if type == "get_all_message":
        gid = datas["gid"]
        message_cur.execute(f"SELECT content, uid, name, unix, number, type FROM {gid}")
        datas = message_cur.fetchall()
        send_datas = []
        for data in datas:
            content, uid, name, unix, number, type = data
            send_datas.append(
                {
                    "content": content,
                    "uid": uid,
                    "name": name,
                    "unix": unix,
                    "number": number,
                    "type": type,
                }
            )
        return {"status": "success", "datas": send_datas}
    else:
        return {"status": "failed", "reason": "invalid type"}

@router.post("/first_forgot_password", response_model=firstForgotPasswordResponse)
def first_forgot_password(raw: firstForgotPassword):
    datas = jsonable_encoder(raw)
    type = datas["type"]
    if type == "first_forgot_password":
        otp = str(uuid.uuid1().int)[:4]
        mail_address = datas["mail_address"]
        cur.execute(f'SELECT email FROM users WHERE email="{mail_address}"')
        exists_mail_address = cur.fetchone()
        print(exists_mail_address)
        if exists_mail_address != None:
            if mail_address not in exists_mail_address:
                return {
                        "status": "failed",
                        "reason": "Email address is invalid or does not exists",
                    }
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
                server = smtplib.SMTP_SSL(
                    "smtp.gmail.com", 465, context=ssl.create_default_context()
                )
                server.login(gmail_account, gmail_password)
                server.send_message(msg)  # メールの送信
                print("ok.")
                return {"status": "success", "uid": uid}
        else:
            return {"status": "failed", "reason": "Any email addresses found"}
    else:
        return {"status": "failed", "reason": "invalid type"} 
@router.post("/forgot_password", response_model=forgotPasswordResponse)
def forgot_password(raw: forgotPassword):
    datas = jsonable_encoder(raw)
    op_type = datas["type"]
    if op_type == "forgot_password":
        otp = int(datas["otp"])
        uid = datas["uid"]
        cur.execute(f'SELECT lastotp FROM users WHERE id="{uid}"')
        lastotp = cur.fetchone()[0]

        if otp == lastotp:
            cur.execute(f'UPDATE users SET lastotp="0" WHERE id="{uid}"')
            conn.commit()
            return {"status": "success"}
        else:
            return {"status": "failed", "reason": "otp is not matched"}
    else:
        return {"status": "failed", "reason": "invalid type"}
@router.post("/reset_password", response_model=statusSuccess)
def reset_password(raw: resetPassword):
    datas = jsonable_encoder(raw)
    op_type = datas["type"]
    if type == "reset_password":
        uid = datas["uid"]
        new_password = datas["new_password"]
        cur.execute(f'SELECT lastotp FROM users WHERE id="{uid}"')
        lastotp = cur.fetchone()[0]
        if lastotp == 0:
            cur.execute(f'UPDATE users SET password="{new_password}" WHERE id="{uid}"')
            conn.commit()
            return {"status": "success"}
        else:
            return {
                    "status": "failed",
                    "reason": "otp was not matched before, or unexpected access from user",
                }
    else:
        return {"status": "failed", "reason": "invalid type"}