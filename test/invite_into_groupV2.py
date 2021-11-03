from login import loginV2
from invite_into_group import invite_into_group

main_uid = loginV2("kjunkiehack@gmail.com", "kouta1014")["uid"]
sub_uid = loginV2("koutamanto@gmail.com", "kouta1014")["uid"]

invite_into_group(main_uid, sub_uid, input("gid:"))