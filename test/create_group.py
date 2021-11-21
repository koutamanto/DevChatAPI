import json
import requests
from login import login
def create_group(name):
  uid = login()["uid"]
  datas = {
    "type": "create_group",
    "uid""": uid,
    "name": name
  }
  r = requests.post(verify=False, url="https://163.44.249.252/create_group", json=datas)
  r_datas = json.loads(r.text)
  print(r, r_datas)
  return r_datas