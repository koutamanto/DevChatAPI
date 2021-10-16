import requests, json
from login import login
from get_list import get_list
datas = login()
uid = datas["uid"]
gids = get_list()
for gid in gids:
    print(gid)
to = input("to(gid):")

while True:
    text = input("text:")
    datas = {"from":uid, "to":to, "message":{"type":"text", "content":text}}
    r = requests.post("http://127.0.0.1/send_message", json=datas)
    print(r, r.text)