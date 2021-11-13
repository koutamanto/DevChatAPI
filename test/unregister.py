import requests, json

datas = {
    "type": "unregister",
    "uid": input("uid:"),
    "password": input("password:")
}

r = requests.post(verify=False, url="https://163.44.249.252/unregister", json=datas)
print(r, r.text)
r_datas = json.loads(r.text)
print(r_datas)