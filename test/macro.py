import requests, json
from login import loginV2
from send_message import send_messageV2

uid = loginV2("kjunkiehack@gmail.com", "kouta1014")["uid"]
gid = input("gid:")
text = input("text:")
for i in range(0, int(input("amount:"))):
    print(i)
    send_messageV2(uid, gid, text)