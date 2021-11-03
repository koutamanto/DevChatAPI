from join_group import join_group
from login import login, loginV2

uid = loginV2("koutamanto@gmail.com", "kouta1014")["uid"]
join_group(uid, input("gid:"))