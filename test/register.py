from flask import json
import requests

datas = {
  "type": "sign_up",
  "user_name": "KJunkie",
  "mail_address": "kjunkiehack@gmail.com",
  "pass_word": "kouta1014"
}
r = requests.post("http://127.0.0.1/register", json=datas)
print(r, r.text)