import json
import requests

def login():
    datas = {
        "type": "log_in",
        "mail_address": "kjunkiehack@gmail.com",
        "pass_word": "kouta1014"
    }

    r = requests.post("http://127.0.0.1/login", json=datas)
    print(r, r.text)
    return json.loads(r.text)