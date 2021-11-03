import requests, json
from config import Config

config = Config()

def leave_group(uid, gid):
    datas = {
        "type": "leave_group",
        "uid":uid,
        "gid":gid
    }
    r = requests.post(config.base_url + "/leave_group", json=datas)
    r_datas = json.loads(r.text)
    print(r, r_datas)
    return r_datas