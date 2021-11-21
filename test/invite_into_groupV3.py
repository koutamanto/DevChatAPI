from login import loginV2
from invite_into_group import invite_into_group

main_uid = loginV2("kjunkiehack@gmail.com", "kouta1014")["uid"]
while True:    
    sub_uid = input("uid:")

    invite_into_group(main_uid, sub_uid, "g56db0108475d11e")