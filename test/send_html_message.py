import requests, json
from login import login
from get_list import get_list
from get_messages import get_messages
def send_html_messageV2(uid, to, content):
    datas = {"type": "send_html_message", "sender":uid, "to":to, "message":{"type":"html", "content":content}}
    r = requests.post(verify=False, url="https://163.44.249.252/send_html_message", json=datas)
    return json.loads(r.text)
    #print(r, r.text)
    #get_messages()