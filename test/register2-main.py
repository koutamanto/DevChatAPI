import requests

uid = input("uid:")
otp = input("otp:")
datas = {
  "type": "sign_up",
  "uid": uid,
  "otp": otp
}

r = requests.post("http://163.44.249.252/register", json=datas)
print(r, r.text)