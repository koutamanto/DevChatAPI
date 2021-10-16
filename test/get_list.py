import requests, json, uuid
from login import login
def get_list():
    datas = login()
    if datas["group"] != []:
        for group in datas["group"]:
            name = group["group_name"]
            gid = group["group_uid"]
            print(name, gid)
    if datas["friend"] != []:
        for friend in datas["friend"]:
            name = friend["friend_name"]
            uid = friend["friend_uid"]
            print(name, uid)
    return datas