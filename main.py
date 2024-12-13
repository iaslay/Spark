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

import numpy as np
import websocket
import openpyxl
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import pickle
from Ws_pararm import PortraitsChat, DoctorChat, Chatbot


def init_question():
    name = input("��������ǣ�")
    age = input("�����ǣ�")
    sex = input("�Ա��ǣ�")
    education = input("���ܽ����̶ȣ�")
    family = input("��ͥ�����Σ�")
    Hobbies = input("��Ȥ�����ǣ�")
    sleep = input("���˯�������Σ�")
    diet = input("�����ʳ�����Σ�")
    motion = input("����˶�������:")
    socializing = input("�罻ϰ�����:")
    medicalhistory = input("���޼�����ʷ,���������뼲�����ƣ�֢״���س̶��Լ����ܹ������ƣ�")
    drugs = input("�������ҩ��ʹ�ã���������ҩ�����ƣ�")
    familymentalhealth = input("����������ʷ��")
    Userportraits = (f'�ҵ�������{name}, ������{age}, �Ա���{sex}�����ܵĽ����̶���{education}, ��ͥ�����{family}, ��Ȥ������{Hobbies}��'
                     f'�����˯�������{sleep}, �����ʳ�����{diet}, �罻ϰ����{socializing}, ����˶������{motion}, �ҵļ�����ʷ��{medicalhistory}'
                     f'�����ʹ��ҩ����{drugs}, ����������ʷ��:{familymentalhealth}')
    return Userportraits

messages = []

def add_message(role, content):
    json_con = {
        "role": role,
        "content": content
    }

    messages.append(json_con)

def get_messages_length(messages):
    length = sum(len(message["content"]) for message in messages)
    return length


# ���token������ȷ������������
def check_messages_length(messages):
    while get_messages_length(messages) > 80000:
        messages.pop(0)
    return messages

def delete_messages(messages):
    del messages[3:]
    return messages


questions = ['�е����˻�����������', '�е������������', '�е�����������', '���ᷳ�����߶����飨������ϲ������Ϸ������Ȥ�½�����ࣿ', '�е����ܴ������л����Ȥ��','�ڴ󲿷������Ｂ���м��ٻ����ࣿ',
'������ͼ��������������', '����ÿ��˯�߶������⣨��˯�����⡱ָ������˯���ѣ���ҹ�������ѵù����˯�ù��ࣩ��', '��ƽʱ˵�����ж�������','���ꡢ�������ܰ��������ţ�',
'�ڴ󲿷�ʱ�䶼�е�ƣ��?', '�ڴ󲿷�ʱ�䶼���Ҹо�����?', '�ڴ󲿷�ʱ�䶼�е��ھΣ�', '���Լ���ע������', '������������', '�о��ܻ���������ϣ���Լ�������', '����˺��Լ���',
               '��������ͷ��', '���ǹ���ɱ��', '������ķ����������ܻ����ʱ���������䡢��Դ󲿷�����ɥʧ��Ȥ�����������Ǹո�̸���Ĵ�������⣿', '����������������������������ȫû������֢״��']

if __name__ == "__main__":
    Doctor = DoctorChat()
    Portraits = PortraitsChat()
    Score = Chatbot({"role": "system", "content": f'��������һ���Ƿ����л����ˣ�����Ҫ�������������Ի������Ƿ��жϡ�����Ҫ����21���жϣ��ֱ��ж��Ƿ��˻����������䡢�Ƿ�е���������顢�Ƿ�е��������ա��Ƿ���ᷳ���������Ȥ�����½����Ƿ��ܴ������л�ȡ��Ȥ���Ƿ��ڴ󲿷������Ｂ���м��ٻ����ࣿ���Ƿ񲻾���ͼ�������������ء��Ƿ񼸺�ÿ��˯�߶������⣨��˯�����⡱ָ������˯���ѣ���ҹ�������ѵù����˯�ù��ࣩ���Ƿ��ƽʱ˵�����ж����������Ƿ��ꡢ�������ܰ��������ţ����Ƿ��ڴ󲿷�ʱ�䶼�е�ƣ��?���Ƿ��ڴ󲿷�ʱ�䶼���Ҹо�����?���Ƿ��ڴ󲿷�ʱ�䶼�е��ھΣ����Ƿ����Լ���ע���������Ƿ����������������Ƿ�о��ܻ���������ϣ���Լ����������Ƿ�����˺��Լ������Ƿ���������ͷ�����Ƿ��ǹ���ɱ�����Ƿ�������ķ����������ܻ����ʱ���������䡢��Դ󲿷�����ɥʧ��Ȥ�����������Ǹո�̸���Ĵ�������⣿���Ƿ�����������������������������ȫû������֢״��. ÿ���жϵõ�һ��0��1���Ƿ��жϸ��ʣ�0����񶨵Ļش�1����϶��Ļش�������ֻ��Ҫ��˳��������ʺ���Ӧ�жϵĽ��ͣ������ʽ���£�1. ���ʣ�0.75 ���ͣ�Lay��Ϊ��ͬѧ����ì�ܶ��е����˺͹¶����������Ŀǰ��һ���̶ȵ��������䡣\n 2. ���ʣ�0.65 ���ͣ������罻���Ѻ���ͬѧ��ì�ܣ�Lay������һ���̶��ϸе���������顣'})
    Summary = Chatbot({"role": "system", "content": f'����Ҫ���⼸�ζԻ��ܽ���������һ�λ�����'})
    portraits = init_question()
    portraits_prompt = Portraits.chat(appid="cc70cb3d",
            api_secret="Y2E5NTM1ODJhMzkxNGZiY2VjMjNjMWEz",
            api_key="ae3e921bff730f27eae0db516238a901",
            Spark_url = "wss://spark-api.xf-yun.com/v4.0/chat",  # 4.0Ultra�����ĵ�ַ
            domain = "4.0Ultra",     # 4.0Ultra �汾
            query=portraits)
    messages.clear()
    add_message('Prompt', portraits_prompt)
    add_message('Summary', '')
    add_message('Question', '')
    for question in questions:
        first = True
        messages[2]['content'] = question
        firstinput = f'�ҵĻ�����Ϣ�ǣ�{messages[0]["content"]}, �Ҹ������ʷ�����¼��{messages[1]["content"]}������������ǿ�ʼ����ɡ�'
        while True:
            if first:
                add_message('user', firstinput)
                print(f"�������Ƿ�{question}")
                add_message('assistant', question)
                first = False
                continue
            else:
                user_query = input("")
                add_message('user', user_query)
            checked_messages = check_messages_length(messages)
            ans = Doctor.chat(
                appid="cc70cb3d",
                api_secret="Y2E5NTM1ODJhMzkxNGZiY2VjMjNjMWEz",
                api_key="ae3e921bff730f27eae0db516238a901",
                Spark_url = "wss://spark-api.xf-yun.com/v4.0/chat",  # 4.0Ultra�����ĵ�ַ
                domain = "4.0Ultra",     # 4.0Ultra �汾
                query=checked_messages
            )
            print(ans)
            if '�����Ի�' in ans:
                summary = 'portraits'+portraits_prompt
                for i in range(len(messages)-3):
                    summary += messages[i+3]['role']
                    summary += messages[i+3]['content']
                summary = Summary.chat(appid="cc70cb3d",api_secret="Y2E5NTM1ODJhMzkxNGZiY2VjMjNjMWEz",api_key="ae3e921bff730f27eae0db516238a901",Spark_url = "wss://spark-api.xf-yun.com/v4.0/chat", domain = "4.0Ultra",query=summary) #���ڵ���������ܽ�
                print(summary)
                messages[1]['content'] = summary
                score = Score.chat(appid="cc70cb3d",api_secret="Y2E5NTM1ODJhMzkxNGZiY2VjMjNjMWEz",api_key="ae3e921bff730f27eae0db516238a901",Spark_url = "wss://spark-api.xf-yun.com/v4.0/chat", domain = "4.0Ultra", query=summary)
                print(score)
                messages = delete_messages(messages)
                print(messages)
                break
            else:
                add_message('assistant', ans)
                # print(ans)


