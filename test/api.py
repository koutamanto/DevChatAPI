import requests, json
from datetime import datetime
from get_messagesV2 import get_messagesV3
from time import sleep
from login import loginV2
from send_message import send_messageV2
from send_html_message import send_html_messageV2
from send_html_with_url import send_html_message_with_urlV2
from get_list import get_listV2

class API:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.uid = self.loginV3()["uid"]
    def run(self, bot):
        self.bot = bot
        while True:     
            self.joined_groups = self.loginV3()["group"]
            for self.group in self.joined_groups:
                sleep(1)
                self.gid = self.group["gid"]
                text = self.get_last_message(self.gid)
                self.bot(text, self.gid)
    def get_last_message(self, gid):
        messages = self.get_messagesV4(gid)
        last_message = messages[-1]
        text = last_message["content"]
        return text
    def loginV3(self):
        return loginV2(self.email, self.password)
    def get_messagesV4(self, gid):
        return get_messagesV3(self.email, self.password, gid)
    def send_messageV3(self, gid, text):
        return send_messageV2(self.uid, gid, text)
    def send_html_messageV3(self,gid, content):
        return send_html_messageV2(self.uid, gid, content)
    def send_html_message_with_urlV3(self, gid, url):
        return send_html_message_with_urlV2(self.uid, gid, url)