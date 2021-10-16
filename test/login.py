import json
import requests

def login():
    datas = {
        "type": "log_in",
        "mail_address": "kjunkiehack@gmail.com",
        "pass_word": "Kouta101466"
    }

    r = requests.post("http://163.44.249.252/login", json=datas)
    print(r, r.text)
    return json.loads(r.text)