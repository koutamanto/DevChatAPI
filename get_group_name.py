import requests, json
from config import Config

def getGroupName(gid):  
    config = Config()
    datas = {
        "type":"get_group_name",
        "gid": gid
    }
    r = requests.post(verify=False, url=config.base_url + "/get_group_name", json=datas)
    result = json.loads(r.text)
    return result