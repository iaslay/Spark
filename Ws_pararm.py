# coding=gb2312
import _thread as thread
import os
import time
import base64
import pandas as pd
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, gpt_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(gpt_url).netloc
        self.path = urlparse(gpt_url).path
        self.gpt_url = gpt_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.gpt_url + '?' + urlencode(v)
        return url


class DoctorChat:
    def __init__(self):
        self.response_content = []

    def on_message(self, ws, message):
        global answer
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            self.response_content.append(content)
            if status == 2:
                ws.close()


    def on_error(self, ws, error):
        print('')

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws):
        thread.start_new_thread(self.run, (ws,))

    def gen_params(self, appid, query, domain):
        """
            通过appid和用户的提问来生成请参数
            """
        system = [{"role": "system", "content": f'你是一个心理陪伴聊天机器人，你需要跟我进行对话判断我是否{query[2]["content"]}。请你基于我的基本信息和历史聊天记录开始聊天，询问我是否{query[2]["content"]}，通过3到5论对话想办法得到答案。当你判断出我确实{query[2]["content"]}，请回复"结束对话"，如果你判断出我并没有{query[2]["content"]}，也请回复"结束对话"'}]
        query = system + query[3:]
        data = {
            "header": {
                "app_id": appid,
                "uid": "1234",
                # "patch_id": []    #接入微调模型，对应服务发布后的resourceid
            },
            "parameter": {
                "chat": {
                    "domain": domain,
                    "temperature": 0.5,
                    "max_tokens": 4096,
                    "auditing": "default",
                }
            },
            "payload": {
                "message": {
                    "text": query
                }
            }
        }
        return data

    def run(self, ws, *args):
        data = json.dumps(self.gen_params(appid=ws.appid, query=ws.query, domain=ws.domain))
        ws.send(data)

    def chat(self, appid, api_secret, api_key, Spark_url, domain, query):
        self.response_content = []
        wsParam = Ws_Param(appid, api_key, api_secret, Spark_url)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close,
                                    on_open=self.on_open)
        ws.appid = appid
        ws.query = query
        ws.domain = domain
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        return ''.join(self.response_content)

class PortraitsChat:
    def __init__(self):
        self.response_content = []
    def on_message(self, ws, message):
        global answer
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            self.response_content.append(content)
            if status == 2:
                ws.close()

    def on_error(self, ws, error):
        print("")

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws):
        thread.start_new_thread(self.run, (ws,))

    def gen_params(self, appid, query, domain):
        """
            通过appid和用户的提问来生成请参数
            """

        data = {
            "header": {
                "app_id": appid,
                "uid": "1234",
                # "patch_id": []    #接入微调模型，对应服务发布后的resourceid
            },
            "parameter": {
                "chat": {
                    "domain": domain,
                    "temperature": 0.5,
                    "max_tokens": 4096,
                    "auditing": "default",
                }
            },
            "payload": {
                "message": {
                    "text":[{"role": "system", "content": f"你将收到一个人的基本信息，你需要用陈述性的更流畅的语句重构这句话"},
                             {"role":'user', 'content':query}
                  ]
                }
            }
        }
        return data

    def run(self, ws, *args):
        data = json.dumps(self.gen_params(appid=ws.appid, query=ws.query, domain=ws.domain))
        ws.send(data)

    def chat(self, appid, api_secret, api_key, Spark_url, domain, query):
        self.response_content = []
        wsParam = Ws_Param(appid, api_key, api_secret, Spark_url)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close,
                                    on_open=self.on_open)
        ws.appid = appid
        ws.query = query
        ws.domain = domain
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        return ''.join(self.response_content)

class Chatbot:
    def __init__(self, system):
        self.response_content = []
        self.system = system

    def on_message(self, ws, message):
        global answer
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            self.response_content.append(content)
            if status == 2:
                ws.close()


    def on_error(self, ws, error):
        print('')

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws):
        thread.start_new_thread(self.run, (ws,))

    def gen_params(self, appid, query, domain):
        """
            通过appid和用户的提问来生成请参数
            """
        data = {
            "header": {
                "app_id": appid,
                "uid": "1234",
                # "patch_id": []    #接入微调模型，对应服务发布后的resourceid
            },
            "parameter": {
                "chat": {
                    "domain": domain,
                    "temperature": 0.5,
                    "max_tokens": 4096,
                    "auditing": "default",
                }
            },
            "payload": {
                "message": {
                    "text": [self.system,
                             {'role': 'user', 'content': query}]
                }
            }
        }
        return data

    def run(self, ws, *args):
        data = json.dumps(self.gen_params(appid=ws.appid, query=ws.query, domain=ws.domain))
        ws.send(data)

    def chat(self, appid, api_secret, api_key, Spark_url, domain, query):
        self.response_content = []
        wsParam = Ws_Param(appid, api_key, api_secret, Spark_url)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close,
                                    on_open=self.on_open)
        ws.appid = appid
        ws.query = query
        ws.domain = domain
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        return ''.join(self.response_content)
