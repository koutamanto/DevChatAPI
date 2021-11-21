import requests
from api import API

cl = API("devchatbot1@gmail.com", "kouta10143")

def bot(text, gid):
    if text == "hi":
        cl.send_messageV3(gid, "hey!!")
    elif text.startswith("get:"):
        url = text.replace("get:", "")
        cl.send_html_message_with_urlV3(gid, url)
    elif text.startswith("mget:"):
        url = text.replace("mget:", "")
        r = requests.get(url=url).text
        cl.send_html_messageV3(gid, r)

cl.run(bot)