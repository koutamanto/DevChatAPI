import requests, json
from login import login

uid = login()["uid"]
datas = {
    "type":"make_folder",
    "uid":uid,
    "name": "テストグループ"
}
r = requests.post(verify=False, url="https://163.44.249.252/make_folder", json=datas)
r_datas = json.loads(r.text)
print(r, r_datas)