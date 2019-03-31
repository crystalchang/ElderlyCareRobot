from telethon import TelegramClient, sync, events
from os import system
from gtts import gTTS as gtts
from pygame import mixer
import speech_recognition as sr
import os
import time
import json
from wit import Wit as wit
import asyncio
import threading
import webbrowser

#################### INITIALISE  ###################
api_id = 524136
api_hash = '84360980c78595ec5fa48af726f8917c'
client = TelegramClient('elcie_client', api_id, api_hash)
loop = asyncio.get_event_loop()
#####################################################

addr_book = {}
# FOR TESTING
#addr_book["daughter"] = 132781136
#addr_book["family"] = 323803805
addr_book["nok"] = []
last_messages = []
last_msg = -1

def add_to_recent(msg_id):
    print("adding to recent")
    print(msg_id)
    last_msg += 1
    if(last_msg == 10):
        last_msg = 0
    print(msg_id)
    last_messages[last_msg] = msg_id
    print(last_messages)


def say(stringToRead):
    tts = gtts(text=repr(stringToRead), lang="en")
    tts.save("tts.mp3")
    mixer.music.load("tts.mp3")
    mixer.music.play()

def repeat_message():
    print("repeating message")
    # change to -1 when using voice
    say(repr(last_messages[-1].message))

async def send_to(person, msg):
    try:
        if "my" in person:
            person = person[3:]
        for chat in addr_book[person]:
            print(" sending" + str(chat) + msg)
            await client.send_message(int(chat),msg)
        return
    except:
        print(person + ' is not in your address book')

async def send_to_id(id, msg):
    try:
        await client.send_message(id,msg)
        return
    except:
        print('error in sending')

async def send_photo(person):
    try:
        if "my" in person:
            person = person[3:]
        chat = addr_book[person]
        await client.send_file(int(chat), "takephoto.png")
        print("sending photo")
    except Exception as e:
        print(e)

# adding relationships using messages
@client.on(events.NewMessage)
async def add_rs_to_addr_book(event):
    msg = str(event.raw_text).lower()
    if ('add relationship' in msg):
        chat = await event.get_chat()
        print('adding relationship')
        segment = msg.split("add relationship ")
        relation = (str(segment[1]))
        if relation == "nok" or "NOK":
            addr_book["nok"].append(chat.id)
        else:
            addr_book[relation] = chat.id
        print(addr_book)
        await client.send_message(chat,"Got it, " + relation + " has been added!")

@client.on(events.NewMessage)
async def add_group_to_addr_book(event):
    msg = str(event.raw_text).lower()
    if 'add group' in msg:
        chat = await event.get_chat()
        print('adding group')
        segment = msg.split("add group ")
        relation = (str(segment[1]))
        addr_book[relation] = chat.id
        await client.send_message(chat,"Okay, group " + relation + " has been added!")
        print(addr_book)

@client.on(events.NewMessage)
async def read_message(event):
    sender = await event.get_sender()
    if (sender.id == 67617730):
        return
    chat = await event.get_chat()
    stringToRead = ""
    stringToRead += "new message from " + str(sender.first_name) + " "
    # from a group chat
    if (chat.id != sender.id):
        stringToRead += " from chat group " + str(chat.title)
    stringToRead += event.raw_text
    say(stringToRead)
    print("new message received")
    last_messages.append(event.message)
    print(last_messages[-1])


#################### VOICE #######################
def handle_message(resp):
    try:
        if "intent" not in resp['entities']:
            say("Sorry, I don't understand your intent.")
            return
        intent = resp['entities']['intent'][0]['value']
        if(intent == "get_help"):
            print("contacting NOK..")
            for nok in addr_book["nok"]:
                loop.create_task(send_to_id(nok, "[IMPT ALERT] Crystal has triggered a help alert. Please respond immediately."))
        elif(intent == "control_appliance"):
            on_off = True if resp['entities']['on_off'][0]['value'] == "on" else False
            appliance = resp['entities']['appliance'][0]['value']
            room = ""
            if "room" in resp:
                room = "in the " + resp['entities']['room'][0]['value']
            if(on_off):
                print("turning on " + appliance + room + "..")
                webbrowser.open("http://127.0.0.1:5000/service/"+appliance)
            else:
                print("turning off " + appliance + room + "..")

        elif(intent == "call"):
            contact = resp['entities']['person'][0]['value']
            print("calling " + contact + "..")

        elif(intent == "send_message"):
            msg = resp['entities']['message_body'][0]['value']
            if 'person' in resp['entities']:
                contact = resp['entities']['person'][0]['value']
                print("sending " + contact + " :" + msg + "..")
                loop.create_task(send_to(contact, msg))
            elif 'group' in resp['entities']:
                contact = resp['entities']['group'][0]['value']
                print("sending " + contact + " :" + msg + "..")
                loop.create_task(send_to(contact, msg))

        elif(intent == "get_weather"):
            # get current location
            if 'datetime' in resp['entitites']:
                date = resp['entities']['datetime'][0]['value']
                print("getting weather for " + date + "..")
            else:
                print("getting weather for today..")
        elif(intent == "repeat_message"):
            repeat_message()
    except KeyError:
        print("Sorry, I could not get the information to complete the action.")

def handle_qr(req):
    if 'photo' in req:
        loop.create_task(send_photo(req[6:]))
    if 'help' in req:
        loop.create_task(send_to("nok", "[IMPT ALERT] Crystal has triggered a help alert. Please respond immediately."))

def recog_callback(r, audio):
    global interpreter
    try:
        transcript = r.recognize_google(audio)
        print(transcript)
        say(repr(transcript))
        resp = interpreter.message(transcript)
        print(resp)
        handle_message(resp)

    except sr.UnknownValueError:
        print("I could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google service; {0}".format(e))

def run():
    global mic
    with mic as source:
        r.adjust_for_ambient_noise(source)

    stop_listening = r.listen_in_background(mic, recog_callback)

def stop():
    stop_listening(wait_for_stop = False)
    time.sleep(1)

def start(queue):
    global r, mic, interpreter
    access_token = 'YQA4LN7PWPCYQDY2YYFVUFTUXKBC4LIB'
    r = sr.Recognizer()
    mic = sr.Microphone()
    interpreter = wit(access_token)

    mixer.init()

    client.start()
    run()
    # requires sign in using phone number
    client.run_until_disconnected()




if __name__ == "__main__":
    threads = []
    try:
        import queue
        my_queue = queue.Queue()
        t = threading.Thread(target = start, args=(my_queue,))
        threads.append(t)
        t.start()
        import qrcodescanner
        t = threading.Thread(target = qrcodescanner.main, args=(my_queue,))
        threads.append(t)
        t.start()

        #handling requests from qrcode scanner
        while (True):
            if (my_queue.empty()):
                continue
            else:
                req = str(my_queue.get())
                print("IN QUEUE" + req)
                handle_qr(req)

    except Exception:
        import traceback
        print(traceback.exc())
