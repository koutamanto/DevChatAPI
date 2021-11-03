import requests, json, uuid
from login import login, loginV2
from pprint import pprint

def get_list():
    datas = login()
    if datas["group"] != []:
        for group in datas["group"]:
            name = group["name"]
            gid = group["gid"]
            print(name, gid)
    if datas["friend"] != []:
        for friend in datas["friend"]:
            name = friend["name"]
            uid = friend["uid"]
            print(name, uid)
    if datas["folder"] != []:
        for folder in datas["folder"]:
            name = folder["name"]
            fid = folder["fid"]
            gids = folder["groups"]
            pprint(name)
            pprint(fid)
            pprint(gids)
    return datas

def get_listV2(email, password):
    datas = loginV2(email, password)
    if datas["group"] != []:
        for group in datas["group"]:
            name = group["name"]
            gid = group["gid"]
            print(name, gid)
    if datas["friend"] != []:
        for friend in datas["friend"]:
            name = friend["name"]
            uid = friend["uid"]
            print(name, uid)
    if datas["folder"] != []:
        for folder in datas["folder"]:
            name = folder["name"]
            fid = folder["fid"]
            gids = folder["groups"]
            pprint(name)
            pprint(fid)
            pprint(gids)
    return datas