import requests, json, uuid
from login import login

#datas = login()
#uid = datas["uid"]
def join_group(uid, gid):
    r = requests.post("http://127.0.0.1/join_group", json={"type":"join_group", "gid":gid , "uid": uid})
    print(r, r.text)