import json, requests

gid = input("gid:")
r = requests.post(verify=False, url="https://163.44.249.252/delete_group", json={"type": "delete_group", "gid":gid})

print(r, r.text)