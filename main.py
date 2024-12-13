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
    name = input("你的名字是：")
    age = input("年龄是：")
    sex = input("性别是：")
    education = input("接受教育程度：")
    family = input("家庭情况如何：")
    Hobbies = input("兴趣爱好是：")
    sleep = input("最近睡眠情况如何：")
    diet = input("最近饮食情况如何：")
    motion = input("最近运动情况如何:")
    socializing = input("社交习惯如何:")
    medicalhistory = input("有无既往病史,若有请输入疾病名称，症状严重程度以及接受过的治疗：")
    drugs = input("最近有无药物使用，若有输入药物名称：")
    familymentalhealth = input("家族心理健康史：")
    Userportraits = (f'我的姓名是{name}, 年龄是{age}, 性别是{sex}，接受的教育程度是{education}, 家庭情况是{family}, 兴趣爱好是{Hobbies}，'
                     f'最近的睡眠情况是{sleep}, 最近饮食情况是{diet}, 社交习惯是{socializing}, 最近运动情况是{motion}, 我的既往病史是{medicalhistory}'
                     f'最近的使用药物是{drugs}, 家族心理健康史是:{familymentalhealth}')
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


# 检查token数量，确保不超过限制
def check_messages_length(messages):
    while get_messages_length(messages) > 80000:
        messages.pop(0)
    return messages

def delete_messages(messages):
    del messages[3:]
    return messages


questions = ['感到悲伤或情绪低落吗？', '感到消沉或空虚吗？', '感到不满或烦恼吗？', '很厌烦，或者对事情（象玩你喜欢的游戏）的兴趣下降了许多？', '感到不能从事物中获得乐趣？','在大部分日子里饥饿感减少或增多？',
'不经意就减轻或增加了体重', '几乎每晚睡眠都有问题（“睡眠问题”指的是入睡困难，半夜醒来，醒得过早或睡得过多）？', '比平时说话或行动缓慢？','烦躁、不安或不能安静地坐着？',
'在大部分时间都感到疲劳?', '在大部分时间都自我感觉不好?', '在大部分时间都感到内疚？', '难以集中注意力？', '难以做决定？', '感觉很坏，以至于希望自己死掉？', '想过伤害自己？',
               '有死的念头？', '考虑过自杀？', '有另外的发作，在两周或更长时间情绪低落、或对大部分事情丧失兴趣，并存在我们刚刚谈到的大多数问题？', '在抑郁发作间期至少有两个月完全没有抑郁症状？']

if __name__ == "__main__":
    Doctor = DoctorChat()
    Portraits = PortraitsChat()
    Score = Chatbot({"role": "system", "content": f'你现在是一个是非评判机器人，你需要根据输入的聊天对话进行是非判断。你需要进行21次判断，分别判断是否悲伤或者情绪低落、是否感到消沉或空虚、是否感到不满或烦恼、是否很厌烦对事情的兴趣有所下降、是否不能从事物中获取乐趣、是否在大部分日子里饥饿感减少或增多？、是否不经意就减轻或增加了体重、是否几乎每晚睡眠都有问题（“睡眠问题”指的是入睡困难，半夜醒来，醒得过早或睡得过多）、是否比平时说话或行动缓慢？、是否烦躁、不安或不能安静地坐着？、是否在大部分时间都感到疲劳?、是否在大部分时间都自我感觉不好?、是否在大部分时间都感到内疚？、是否难以集中注意力？、是否难以做决定？、是否感觉很坏，以至于希望自己死掉？、是否想过伤害自己？、是否有死的念头？、是否考虑过自杀？、是否有另外的发作，在两周或更长时间情绪低落、或对大部分事情丧失兴趣，并存在我们刚刚谈到的大多数问题？、是否在抑郁发作间期至少有两个月完全没有抑郁症状？. 每次判断得到一个0到1的是非判断概率，0代表否定的回答，1代表肯定的回答。最终你只需要按顺序输出概率和相应判断的解释，输出格式如下：1. 概率：0.75 解释：Lay因为与同学发生矛盾而感到悲伤和孤独，这表明他目前有一定程度的情绪低落。\n 2. 概率：0.65 解释：由于社交困难和与同学的矛盾，Lay可能在一定程度上感到消沉或空虚。'})
    Summary = Chatbot({"role": "system", "content": f'你需要将这几段对话总结起来，用一段话描述'})
    portraits = init_question()
    portraits_prompt = Portraits.chat(appid="cc70cb3d",
            api_secret="Y2E5NTM1ODJhMzkxNGZiY2VjMjNjMWEz",
            api_key="ae3e921bff730f27eae0db516238a901",
            Spark_url = "wss://spark-api.xf-yun.com/v4.0/chat",  # 4.0Ultra环境的地址
            domain = "4.0Ultra",     # 4.0Ultra 版本
            query=portraits)
    messages.clear()
    add_message('Prompt', portraits_prompt)
    add_message('Summary', '')
    add_message('Question', '')
    for question in questions:
        first = True
        messages[2]['content'] = question
        firstinput = f'我的基本信息是：{messages[0]["content"]}, 我跟你的历史聊天记录是{messages[1]["content"]}，基于这个我们开始聊天吧。'
        while True:
            if first:
                add_message('user', firstinput)
                print(f"请问你是否{question}")
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
                Spark_url = "wss://spark-api.xf-yun.com/v4.0/chat",  # 4.0Ultra环境的地址
                domain = "4.0Ultra",     # 4.0Ultra 版本
                query=checked_messages
            )
            print(ans)
            if '结束对话' in ans:
                summary = 'portraits'+portraits_prompt
                for i in range(len(messages)-3):
                    summary += messages[i+3]['role']
                    summary += messages[i+3]['content']
                summary = Summary.chat(appid="cc70cb3d",api_secret="Y2E5NTM1ODJhMzkxNGZiY2VjMjNjMWEz",api_key="ae3e921bff730f27eae0db516238a901",Spark_url = "wss://spark-api.xf-yun.com/v4.0/chat", domain = "4.0Ultra",query=summary) #基于单次聊天的总结
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


