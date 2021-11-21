# DevChatAPI
API for DevChat BackEnd.

Created By KJunkie Using Python/Flask/SQLite3/Requests/JSON etc.
## Functions
### Account
- Sign Up
- Login(get friend & group list)
- Forgot Password(Change Password)

### Group
- Upload Group Icon(Change)
- Create group
- Delete Group
- Join Group
- Invite Into Group
- Leave Group
### Folder

- Make Folder
- Put Into Folder
- Delete Folder

### Message
- Send message(Text)
- Get messages

### User
- Upload User Icon(Change)
- Add Friend
### If body of request has no or invalid type param:
```
{
  "status":"failed",
  "reason":"invalid type"
}
```

## Requests
### Sign Up

#### Before OTP Authentication
URL : /register

##### Required Params

- type
  - "first_sign_up"
- user_name
- mail_address
  - "user@example.com"
- pass_word
  - "example1234"

Request JSON : 
```
{
  "type": "first_sign_up",
  "user_name": "User Name",
  "mail_address": "user@example.com",
  "pass_word": "example1234"
}
```

Response JSON:
```
{
  "uid":"u1234567890abcde" # "u" + 15 digits hex = 16 digits uid
}
```



Sample:https://github.com/koutamanto/DevChatAPI/blob/main/test/register3.py

#### After OTP Authentication
URL : /register

##### Required Params
- type
  - "sign_up"
- uid
  - "u1234567890abcde" #got from response of "Before OTP"
- otp
  - 1234 #got from OTP mail

Request JSON
```
{
  "type": "sign_up",
  "uid": "u1234567890abcde",
  "otp": "1234"
}
```

Response JSON
```
{
  "uid":"u1234567890abcde" # "u" + 15 digits hex = 16 digits uid
}
```

### Login

URL : /login

#### Required Params
- type
  - "log_in"
- mail_address
  - "user@example.com"
  - "example1234"

```
{
  "type": "log_in",
  "mail_address": "user@example.com",
  "pass_word": "example1234"

```
Response JSON(friend & group list):
```
{
    "folders":[
        {
            "fid": "folder`s id", 
            "name": "folder`s name",
            "groups": [
                "gid",
                "gid",
                "gid",
                "gid",
                "gid"
            ]
        }
    ],
    "groups": [
        {
            "gid": "gid",
            "name": "group name",
            "icon_url": "http://example.icon.url.dev/"
        }
    ],
    "friends": [
        {"uid": "uid", "name": "friend name", "icon_url": "http://example.icon.url.dev/"}, //友達登録してある人
        {"uid": "uid", "name": "friend name", "icon_url": "http://example.icon.url.dev/"},
        {"uid": "uid", "name": "friend name", "icon_url": "http://example.icon.url.dev/"},
        {"uid": "uid", "name": "friend name", "icon_url": "http://example.icon.url.dev/"}
    ]
}
```

Sample:https://github.com/koutamanto/DevChatAPI/blob/main/test/login.py

### Forgot Password

#### Before OTP
URL: /forgot_password

##### Required Params
- type
  - "first_forgot_password"
- mail_address
  - "user@example.com"

Request JSON:
```
{
  "type": "firt_forgot_password",
  "mail_address": "user@example.com"
}
```

Response JSON:
```
{
  "uid":"u1234567890abcde" # "u" + 15 digits hex = 16 digits uid
}
```

#### Send OTP

##### Required Params
- type
  - "forgot_password"
- uid
  - "u1234567890abcde"
- otp
  - 1234

Request JSON:
```
{
  "type": "forgot_password",
  "uid":"u1234567890abcde" # "u" + 15 digits hex = 16 digits uid
  "otp":1234
}
```

Response JSON:

(OTP Authentication Success):
```
{
  "status":"success"
 }
```

((OTP Authentication Failed):
```
{
  "status":"failed", 
  "reason":"otp is not matched"
 }
```


### Reset Password

##### Required Params
- type
  - "reset_password"
- uid
  - "u1234567890abcde"
- new_password
  - "unko1234"

Request JSON:

```
{
  "type": "reset_password",
  "uid": "u1234567890abcde",
  "new_password": "unko1234"

```
Response JSON:

(Success):
```
{
  "status":"success"
}

```

(Failed):
```
{
  "status":"failed", 
  "reason":"otp was not matched before, or unexpected access from user"
}
```

### Group

#### Create Group

URL: /create_group

Request JSON
```
{
  "type": "create_group",
  "sender": "u1234567890abcde",
  "name": "グループ名"
}
```

Response JSON
```
{
  "gid":"g1234567890abcde"
}
```

#### Delete Group

URL: /delete_group

Request JSON
```
{
  "type": "delete_group",
  "gid":"g1234567890abcde"
}
```

Response JSON
```
{
  "status":"success"
}
```

#### Join Group

URL: /join_group

Request JSON
```
{
  "type": "join_group", 
  "gid": "g1234567890abcde" , 
  "uid": "u1234567890abcde"
}
```

Response JSON
```
{
  "status": "success"
}
```

#### Invite Into Group

URL: /invite_into_group

Request JSON
```
{
  "type": "invite_into_group",
  "target_uid": "u1029384857abdecd", #招待する対象のuid
  "to": "g1234567890abcde", #招待先のグループのgid
  "uid": "u1234567890abcde" #自分のuid
}
```

Response JSON
```
{
  "gid": "g1234567890abcde" #招待が成功したグループのgid
}
```

#### Upload Group Icon(Change)

URL: /upload_group_icon

Request JSON:
```
{
    "type":"upload_group_icon",
    "gid":"g1234567890abcde" #gid,
    "content": "afhsvuBNUJHr84759FHJRF89..." #base64 encoded image str,
    "filename": "g1234567890abcde.png" #(gid + ".png)
}
```

Response JSON:
```
{
  "status":"success",
  "icon_url": "http://163.44.249.252/images/g1234567890abcde.png" #icon_url
}
```

#### Leave Group

URL: /leave_group

Request JSON:
```
{
  "type": "leave_group",
  "uid":"u1234567890abcde",
  "gid":"g1234567890"
}
```

Response JSON:

```
{
  "status":"success"
}
```

### Folder

#### Make Folder

URL: /make_folder

Request JSON:
```
{
    "type":"make_folder",
    "uid": "u1234567890abcde",
    "name": "フォルダー名"
}
```

Response JSON:
```
{
  "status":"success",
  "fid": "f1234567890abcde"
}
```

#### Put Into Folder

URL: /put_into_folder

Request JSON:
```
{
    "type":"put_into_folder",
    "uid": "u1234567890abcde",
    "gid": "g1234567890abcde",
    "fid": "f1234567890abcde"
}
```

#### Delete Folder

URL: /delete_folder

Request JSON:
```
{
    "type":"delete_folder",
    "uid":"u1234567890abcde",
    "fid":"f1234567890abcde"
}
```

### Message

#### Send Message(Text)

URL: /send_text_message

Request JSON:
```
{
  "sender": "u1234567890abcde", 
  "to":"g1234567890abcde",
  "message":{
    "type":"text", 
    "content":"こんにちは" #メッセージ内容
   }
}
```

Response JSON:
```
{
  "status":"success"
}
```

#### Send Message(Image)

URL: /send_image_message

Request JSON:
```
{
  "sender": "u1234567890abcde",
  "to": "g1234567890abcde",
  "message": {
    "type": "image",
    "content": "byte codes" #base64でエンコードした画像のバイトコード
    }
}
```

Response JSON:
```
{
  "status":"success", 
  "type":"image", 
  "url":"http://devchat.jp/images/ファイル名.拡張子" #例:"http://devchat.jp/images/Unko931.png"
}
```

#### Get Messages

URL: /get_all_message

Request JSON:
```
{
  "type":"get_all_message", 
  "gid":"g1234567890abcde")
}
```

Response JSON:
```
{
  "datas":[
    {
      "content":"こんにちは", 
      "uid": "u1029384756abced", 
      "name": "通りすがりのユーザー", 
      "unix": 1634343835.846011, 
      "number": 1
    },
    {
      "content":"こんにちは", 
      "uid": "u1029384756abced", 
      "name": "逆張り挨拶おじさん", 
      "unix": 1634343840.12345, 
      "number": 2
    }
  ]
}
```

URL: /get_recent_message

Request JSON:
```
{
  "type":"get_recent_message", 
  "gid":"g1234567890abcde")
}
```

Response JSON:
```
{
  "datas":[
    {
      "content":"こんにちは", 
      "uid": "u1029384756abced", 
      "name": "通りすがりのユーザー", 
      "unix": 1634343835.846011, 
      "number": 80 #最新から100件前
    },
    {
      "content":"こんにちは", 
      "uid": "u1029384756abced", 
      "name": "逆張り挨拶おじさん", 
      "unix": 1634343840.12345, 
      "number": 81
    }
  ]
  ...
      {
      "content":"最新のメッセージだヨ！",
      "uid": "u1029384756abced", 
      "name": "最新おじさん", 
      "unix": 1634343840.12345, 
      "number": 180
    }
  ]
}
```

### User

#### Upload User Icon(Change)

URL: /upload_icon

Request JSON:
```
{
    "type":"upload_icon",
    "uid":"u1234567890abcde",
    "content": "ASujbnfvdsohjboAEFOUHjb==..." #base64 encoded image str,
    "filename": "u1234567890abcde.png" #uid + ".png"

}
```

Response JSON:
```
{
  "status":"success",
  "icon_url": "http://163.44.249.252/images/u1234567890abcde.png" #icon_url
}
```

#### Add Friend

URL: /add_friend

Request JSON:
```
{
  "type": "add_friend",
  "from_uid":"u1234567890abcde", #sender mid
  "target_uid":"u10293847856aedcd" #target mid to add
}
```

Response JSON:
{
  "status": "success",
  "target_uid": target_uid
}
