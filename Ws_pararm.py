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
    # ��ʼ��
    def __init__(self, APPID, APIKey, APISecret, gpt_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(gpt_url).netloc
        self.path = urlparse(gpt_url).path
        self.gpt_url = gpt_url

    # ����url
    def create_url(self):
        # ����RFC1123��ʽ��ʱ���
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # ƴ���ַ���
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # ����hmac-sha256���м���
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # ������ļ�Ȩ�������Ϊ�ֵ�
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # ƴ�Ӽ�Ȩ����������url
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
            print(f'�������: {code}, {data}')
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
            ͨ��appid���û������������������
            """
        system = [{"role": "system", "content": f'����һ�����������������ˣ�����Ҫ���ҽ��жԻ��ж����Ƿ�{query[2]["content"]}����������ҵĻ�����Ϣ����ʷ�����¼��ʼ���죬ѯ�����Ƿ�{query[2]["content"]}��ͨ��3��5�۶Ի���취�õ��𰸡������жϳ���ȷʵ{query[2]["content"]}����ظ�"�����Ի�"��������жϳ��Ҳ�û��{query[2]["content"]}��Ҳ��ظ�"�����Ի�"'}]
        query = system + query[3:]
        data = {
            "header": {
                "app_id": appid,
                "uid": "1234",
                # "patch_id": []    #����΢��ģ�ͣ���Ӧ���񷢲����resourceid
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
            print(f'�������: {code}, {data}')
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
            ͨ��appid���û������������������
            """

        data = {
            "header": {
                "app_id": appid,
                "uid": "1234",
                # "patch_id": []    #����΢��ģ�ͣ���Ӧ���񷢲����resourceid
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
                    "text":[{"role": "system", "content": f"�㽫�յ�һ���˵Ļ�����Ϣ������Ҫ�ó����Եĸ�����������ع���仰"},
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
            print(f'�������: {code}, {data}')
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
            ͨ��appid���û������������������
            """
        data = {
            "header": {
                "app_id": appid,
                "uid": "1234",
                # "patch_id": []    #����΢��ģ�ͣ���Ӧ���񷢲����resourceid
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
