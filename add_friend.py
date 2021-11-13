import requests, json
from config import Config

def add_friend(from_uid, target_uid):
    datas = {
        "type": "add_friend",
        "from_uid":from_uid,
        "target_uid":target_uid
    }
    r = requests.post(verify=False, url=Config().base_url + "/add_friend", json=datas)
    r_datas = json.loads(r.text)
    print(r, r_datas)
    return r_datas