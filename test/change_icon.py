import base64
from io import BytesIO
import requests, json
from login import login, loginV2
from config import Config

from PIL import Image


config = Config()

uid = loginV2("koutamanto@gmail.com", "kouta1014")["uid"]

img = Image.open("icon_medical_woman03.png")
buffered = BytesIO()
img.save(buffered, format="PNG")
img_byte = buffered.getvalue() # bytes
img_base64 = base64.b64encode(img_byte) # base64でエンコードされたbytes ※strではない
# まだbytesなのでjson.dumpsするためにstrに変換(jsonの要素はbytes型に対応していないため)
img_str = img_base64.decode('utf-8') 

datas = {
    "type":"upload_icon",
    "uid":uid,
    "content": img_str,
    "filename": uid + ".png"

}

r = requests.post(config.upload_icon_url, json=datas)
r_datas = json.loads(r.text)
print(r, r_datas)