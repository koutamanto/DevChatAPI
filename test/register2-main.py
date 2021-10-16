import requests

uid = input("uid:")
otp = input("otp:")
datas = {
  "type": "sign_up",
  "uid": uid,
  "otp": otp
}

r = requests.post("http://127.0.0.1/register", json=datas)
print(r, r.text)