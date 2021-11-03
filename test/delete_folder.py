import requests, json
from login import login

#uid = login()["uid"]
datas = {
    "type":"delete_folder",
    "uid":"u7bd413bc2e1411e",
    "fid":"f02d25536377011e	"
}
r = requests.post("http://163.44.249.252/delete_folder", json=datas)
r_datas = json.loads(r.text)
print(r, r_datas)