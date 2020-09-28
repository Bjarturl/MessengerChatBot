import os
import json
import shutil
import re
from functools import partial
import random

#Cleans and uses data from Facebook Messenger to create a simple chat bot based on answers to messages
file_handles = {}

def fixText(path): #Fix encoded text to UTF-8 format
    try:
        fix_mojibake_escapes = partial(
            re.compile(rb'\\u00([\da-f]{2})').sub,
            lambda m: bytes.fromhex(m.group(1).decode()))
        with open(path, 'rb') as f:
            repaired = fix_mojibake_escapes(f.read())
        return json.loads(repaired.decode('utf8'))
    except:
        return {}

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  
        u"\U0001F300-\U0001F5FF"  
        u"\U0001F680-\U0001F6FF"  
        u"\U0001F1E0-\U0001F1FF"  
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)


def get_responses(path, corpus_path):
    data = fixText(path + 'message_1.json')
    if not os.path.exists(corpus_path):
        os.mkdir(corpus_path)
    if 'participants' not in data:
        return
    for participant in data['participants']:
        participant_name = participant['name'].replace(' ', '_').lower()
        file_handles[participant_name] = open(corpus_path + '/' + participant_name + '.txt', 'a', encoding="utf-8")
    prev_msg = None
    prev_sender = None
    for message in reversed(data['messages']):
        if 'content' in message \
            and message['type']== 'Generic' \
            and message['content'].find('http') == -1 \
            and message['content'].find('sent a photo') == -1 \
            and message['content'].find('set his own nickname') == -1 \
            and message['content'].find('set the emoji to') == -1 \
            and message['content'].find('set your nickname to') == -1 \
            and message['content'].find('named the group') == -1 \
            and message['content'].find('removed vote for') == -1 \
            and message['content'].find('voted for') == -1 \
            and message['content'].find('created a poll') == -1 \
            and message['content'].find('updated the plan') == -1 \
            and message['content'].find('set the nickname for') == -1 \
            and message['content'].find('created the group') == -1 \
            and message['content'].find('set the group photo') == -1:
            try:
                content = message['content'].lower().replace('\u00f0\u009f\u0098\u009b', ':p')
                content = deEmojify(content)
                sender_name = message['sender_name'].replace(' ', '_').lower()
                if prev_msg and prev_sender and prev_sender != sender_name:
                    file_handles[sender_name].write(prev_msg + " ||||| " + content + "\n"
                    )
                if prev_sender == sender_name:
                    prev_msg += content
                else:
                    prev_msg = content
                prev_sender = sender_name
                
            except:
                pass

def get_individuals(path, corpus_path):
    for p in os.listdir(path):
        get_responses(path + p + "/", corpus_path)


def createChatBot(path, corpus_path, name):
    responses = {}
    with open(corpus_path + name + ".txt", "r", encoding="utf8") as f:
        for t in f.readlines():
            try:
                prev, answer = t.replace("\n", "").split("|||||")
                prev = prev.strip().lower()
                answer = answer.strip().lower()
                if prev not in responses:
                    responses[prev] = []
                responses[prev].append(answer)
            except:
                pass
    return responses

def chat(path, corpus_path):
    chatbot = createChatBot(path, corpus_path, "bjartur_lúkas_grétarsson")
    me = "Bjartur says: "
    print(me + "hallo")
    while True:
        msg = input("You: ").strip().lower()
        if msg == "hætta":
            break
        if msg not in chatbot:
            print(me + "hvernig á ég að svara þessu??")
        else:
            print(me + random.choice(chatbot[msg]))


path = os.getcwd() + '/all_messages/messages/inbox/'
corpus_path = os.getcwd() + '/corpus_responses/'
get_responses(path, corpus_path)
chat(path, corpus_path)
