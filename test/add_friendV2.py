from login import loginV2
from add_friend import add_friend

main_uid = loginV2("kjunkiehack@gmail.com", "kouta1014")["uid"]
sub_uid = loginV2("koutamanto@gmail.com", "kouta1014")["uid"]

datas = add_friend(main_uid, sub_uid)