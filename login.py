import json
import requests

def login():
    datas = {
        "type": "log_in",
        "mail_address": "kjunkiehack@gmail.com",
        "pass_word": "kouta1014"
    }

    r = requests.post(verify=False, url="https://devchat.jp/login", json=datas)
    #print(r, json.loads(r.text))
    return json.loads(r.text)
def loginV2(email, password):
    datas = {
        "type": "log_in",
        "mail_address": email,
        "pass_word": password
    }
    r = requests.post(verify=False, url="https://devchat.jp/login", json=datas)
    #print(r, json.loads(r.text))
    return json.loads(r.text)