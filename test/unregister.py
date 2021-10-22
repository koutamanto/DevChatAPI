import requests, json

datas = {
    "type": "unregister",
    "uid": input("uid:")
}

r = requests.post("http://163.44.249.252/unregister", json=datas)
print(r, r.text)
r_datas = json.loads(r.text)
print(r_datas)