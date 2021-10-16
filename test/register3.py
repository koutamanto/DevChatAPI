import requests

user_name = input("[1/5] user_name:")
email = input("[2/5] email:")
pass_word = input("[3/5] pass_word:")

datas_for_first = {
  "type": "first_sign_up",
  "user_name": user_name,
  "mail_address": email,
  "pass_word": pass_word
}

r = requests.post("http://127.0.0.1/register", json=datas_for_first)
print(r, r.text)

uid = input("[4/5] uid:")
otp = input("[5/5] otp:")
datas = {
  "type": "sign_up",
  "uid": uid,
  "otp": otp
}

r = requests.post("http://127.0.0.1/register", json=datas)
print(r, r.text)