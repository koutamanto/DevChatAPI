import requests, json
from login import login
from get_list import get_list
from get_messages import get_messages

def send_html_message_with_urlV2(uid, to, url):
    datas = {"type": "send_html_message_with_url", "sender":uid, "to":to, "message":{"type":"html_url", "content":url}}
    r = requests.post(verify=False, url="https://163.44.249.252/send_html_message_with_url", json=datas)
    return json.loads(r.text)
    #print(r, r.text)
    #get_messages()