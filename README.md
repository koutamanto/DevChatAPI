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

```
{
  "type": "sign_up",
  "uid": "u1234567890abcde",
  "otp": "1234"
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

Sample:https://github.com/koutamanto/DevChatAPI/blob/main/test/login.py
