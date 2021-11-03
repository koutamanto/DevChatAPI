import base64
from io import BytesIO
import requests, json
from login import login, loginV2
from config import Config

from PIL import Image


config = Config()

uid = loginV2("kjunkiehack@gmail.com", "kouta1014")["uid"]

img = Image.open("no-translate-detected_318-27951.jpg")
buffered = BytesIO()
img.save(buffered, format="PNG")
img_byte = buffered.getvalue() # bytes
img_base64 = base64.b64encode(img_byte) # base64でエンコードされたbytes ※strではない
# まだbytesなのでjson.dumpsするためにstrに変換(jsonの要素はbytes型に対応していないため)
img_str = img_base64.decode('utf-8') 

gid = "gcb362e683c3d11e"

datas = {
    "type":"upload_group_icon",
    "gid":gid,
    "content": img_str,
    "filename": gid + ".png"

}

r = requests.post(config.base_url + "/upload_group_icon", json=datas)
r_datas = json.loads(r.text)
print(r, r_datas)