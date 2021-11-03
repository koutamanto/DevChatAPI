from login import loginV2
from leave_group import leave_group
from get_list import get_listV2

uid = loginV2("kjunkiehack@gmail.com", "kouta1014")["uid"]
while True:
    get_listV2("kjunkiehack@gmail.com", "kouta1014")
    leave_group(uid, input("gid:"))