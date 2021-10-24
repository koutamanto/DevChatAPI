import requests
from login import login

uid = login()["uid"]
datas = {
  "type": "create_group",
  "from": uid,
  "name": "画像送信テストぐる"
}
r = requests.post("http://163.44.249.252/create_group", json=datas)
print(r, r.text)