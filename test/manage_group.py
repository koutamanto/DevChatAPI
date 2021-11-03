from requests.api import get
from join_group import join_group
from get_list import get_list
from create_group import create_group
import requests, json

while True:
    datas = get_list()
    op = input("join_group[j]/create_group[c] :")
    if op == "j":
        uid = datas["uid"]
        join_group(uid, input("[join_group] gid:"))
    if op == "c":
        create_group(input("[create_group] group_name:"))