import requests, json

datas = {
    "type":"get_group_name",
    "gid": "gc8df850644f311e"
}

raw = requests.post("https://devchat.jp/get_group_name", json=datas)
print(raw, json.loads(raw.text))