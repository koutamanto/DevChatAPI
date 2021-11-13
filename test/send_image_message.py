import requests
from PIL import Image
import json
import base64
from io import BytesIO

from login import login

uid = login()["uid"]
img = Image.open("250px-KRSW.png")
buffered = BytesIO()
img.save(buffered, format="PNG")
img_byte = buffered.getvalue() # bytes
img_base64 = base64.b64encode(img_byte) # base64でエンコードされたbytes ※strではない
# まだbytesなのでjson.dumpsするためにstrに変換(jsonの要素はbytes型に対応していないため)
img_str = img_base64.decode('utf-8') # str
datas = {"from":uid, "to":"g2b5f30a6347c11e", "message": {"type":"image", "content": img_str, "filename":"250px-KRSW.png"}}
print(datas)
r = requests.post(verify=False, url="https://163.44.249.252/send_image_message", json=datas)
print(r, r.text)
r_datas = json.loads(r.text)
print(r_datas)