from login import loginV2
from add_friend import add_friend

main_uid = loginV2("kjunkiehack@gmail.com", "kouta1014")["uid"]
sub_uid = "uaa40e1d4402111e"

datas = add_friend(main_uid, sub_uid)