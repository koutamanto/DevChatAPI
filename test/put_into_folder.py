import requests, json
from login import login
from get_list import get_list

uid = login()["uid"]
talk_list = get_list()

datas = {
    "type":"put_into_folder",
    "uid": uid,
    "gid": input("gid:"),
    "fid": input("fid:")
}
r = requests.post(verify=False, url="https://163.44.249.252/put_into_folder", json=datas)
r_datas = json.loads(r.text)
print(r, r_datas)