import requests, json
from login import login

def get_messages():    
    datas = login()

    for group in datas["group"]:
        gid = group["gid"]
        print(gid)
    r = requests.post(verify=False, url="https://163.44.249.252/get_message", json={"type":"get_message", "gid":input("gid:")})
    r_datas = json.loads(r.text)["datas"]
    print(r, r_datas)
    for message in r_datas:
        content = message["content"]
        name = message["name"]
        uid = message["uid"]
        number = message["number"]
        unix = message["unix"]
        print(content, name, uid, number, unix)