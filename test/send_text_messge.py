import requests, json, uuid
from login import login
#uuid32 = str(uuid.uuid1().hex)
#uid = uuid32[:16]
#print(uuid32, uid)
#uuid32 = str(uuid.uuid1().hex)
#gid = uuid32[:16]
#text = "hey"
datas = login()
uid = datas["uid"]
#gid = "g88dfba6a2d9811e"
gid = "g2269baca2d9c11e"
text = input("text:")
datas = {"from":uid, "to":gid, "message":{"type":"text", "content":text}}
r = requests.post("http://127.0.0.1/send_message", json=datas)
print(r, r.text)