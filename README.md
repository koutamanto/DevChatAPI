# DevChatAPI
API for DevChat BackEnd.

Created By KJunkie Using Python/Flask/SQLite3/Requests/JSON etc.
## Functions
### Account
- Sign Up
- Login(get friend & group list)
- Forgot Password(Change Password)

### Group

- Create group
- Delete Group
- Join Group

### Message
- Send message(Text)
- Get messages

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
  "friend": [
    {"friend_uid":"u0987654321abcde", "friend_name": "ともさん"},
    {"friend_uid":"u1029384756abedc", "friend_name": "かっちゃん"}
  ],
  "group": [
    {"group_uid":"g1234567890abcde", "friend_name": "一関高専焼肉部"},
    {"group_uid":"g01928dd464ffdca", "friend_name": "椅子の足ファンクラブ"}
  ]
  "uid":"u1234567890abcde" # "u" + 15 digits hex = 16 digits uid
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

