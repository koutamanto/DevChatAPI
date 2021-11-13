import requests, json
from config import Config

config = Config()

def invite_into_group(uid, target_uid, to):
    datas = {
        "type":"invite_into_group",
        "uid": uid,
        "target_uid":target_uid,
        "to": to
    }
    r = requests.post(verify=False, url=config.base_url + "/invite_into_group", json=datas)
    r_datas = json.loads(r.text)
    print(r, r_datas)
    return r_datas