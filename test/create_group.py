import requests

datas = {
  "type": "create_group",
  "from": "9b6c12762d7c11ec",
  "name": "テスト用のグループ"
}
r = requests.post("http://163.44.249.252/create_group", json=datas)
print(r, r.text)