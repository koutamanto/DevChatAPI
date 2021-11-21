import requests, json
from login import login
from get_list import get_list
from get_messages import get_messages

datas = login()
uid = datas["uid"]
gids = get_list()
for gid in gids:
    print(gid)
to = input("to(gid):")

while True:
    text = input("text:")
    datas = {"sender":uid, "to":to, "message":{"type":"text", "content":text}}
    r = requests.post(verify=False, url="https://163.44.249.252/send_text_message", json=datas)
    print(r, r.text)
    get_messages()