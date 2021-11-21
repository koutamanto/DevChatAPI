import requests, json
from datetime import datetime
from get_messagesV2 import get_messagesV3
from time import sleep
from login import loginV2
from send_message import send_messageV2
from send_html_message import send_html_messageV2
from send_html_with_url import send_html_message_with_urlV2
from get_list import get_listV2

cl_uid = loginV2("devchatbot1@gmail.com", "kouta10143")["uid"]
while True:
    #try:
    sleep(1)
    joined_groups = loginV2("devchatbot1@gmail.com", "kouta10143")["group"]
    for group in joined_groups:
        sleep(1)
        gid = group["gid"]
        messages = get_messagesV3("devchatbot1@gmail.com", "kouta10143", gid)
        last_message = messages[-1]
        text = last_message["content"]
        if text == "こんにちは":
            send_messageV2(cl_uid, gid, "こんにちは～")
        elif text == "おはよう":
            send_messageV2(cl_uid, gid, "は？(困惑)")
        elif text.startswith("get:"):
            url = text.replace("get:", "")
            print(url)
            send_html_message_with_urlV2(cl_uid, gid, url)
        elif text.startswith("mget:"):
            url = text.replace("mget:", "")
            r = requests.get(url=url).text
            send_html_messageV2(cl_uid, gid, r)
        elif text in ["now", "今何時？", "現在時刻"]:
            send_messageV2(cl_uid, gid, datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
    #except Exception as e:
    #    print(e)