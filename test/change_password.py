import requests, json
from login import login

datas = login()
uid = datas["uid"]
first_datas = {"type":"first_forgot_password", "mail_address": "kjunkiehack@gmail.com"}
r = requests.post("http://163.44.249.252/forgot_password", json=first_datas)
print(r, r.text)
otp = input("otp:")
forgot_datas = {"type":"forgot_password", "otp":otp, "uid":uid}
r = requests.post("http://163.44.249.252/forgot_password", json=forgot_datas)
print(r, r.text)
received_datas = json.loads(r.text)
if received_datas["status"] == "success":
    new_password = input("new_password:")
    reset_datas = {"type":"reset_password", "uid":uid, "new_password": new_password}
    r = requests.post("http://163.44.249.252/forgot_password", json=reset_datas)
    print(r, r.text)