import json, requests

gid = "g88dfba6a2d9811e"
r = requests.post("http://127.0.0.1/delete_group", json={"type": "delete_group", "gid":gid})

print(r, r.text)