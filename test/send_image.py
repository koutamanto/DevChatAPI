import requests, json


with open("test.png", "rb") as image_file:

    datas = {
        "sender": input("uid:"),
        "to": input("to:"),
        "message": {
            "type": "image",
            "content": image_file.read()
        }
    }

r = requests.post(verify=False, url="https://163.44.249.252/send_image_message", json=datas)
print(r, r.text)
r_datas = json.loads(r.text)
print(r_datas)