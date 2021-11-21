import requests, json
from config import Config

config = Config()

def leave_group(uid, gid):
    datas = {
        "type": "leave_group",
        "uid":uid,
        "gid":gid
    }
    r = requests.post(verify=False, url="https://163.44.249.252" + "/leave_group", json=datas)
    r_datas = json.loads(r.text)
    print(r, r_datas)
    return r_datas