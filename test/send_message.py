import requests, json
from login import login
from get_list import get_list
from get_messages import get_messages
def send_messageV2(uid, to, text):
    datas = {"sender":uid, "to":to, "message":{"type":"text", "content":text}}
    r = requests.post(verify=False, url="https://163.44.249.252/send_text_message", json=datas)
    return json.loads(r.text)
    #print(r, r.text)
    #get_messages()