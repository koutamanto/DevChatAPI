import requests, json
from login import login

def get_messagesV2(gid):    
    datas = login()

    r = requests.post(verify=False, url="https://163.44.249.252/get_recent_message", json={"type":"get_recent_message", "gid":gid})
    r_datas = json.loads(r.text)["datas"]
    return r_datas
#    print(r, r_datas)
#    for message in r_datas:
#        content = message["content"]
#        name = message["name"]
#        uid = message["uid"]
#        number = message["number"]
#        unix = message["unix"]
#        print(content, name, uid, number, unix)