import requests

datas = {
  "type": "create_group",
  "from": "9b6c12762d7c11ec",
  "name": "テスト用のグループ"
}
r = requests.post("http://127.0.0.1/create_group", json=datas)
print(r, r.text)