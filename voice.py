import speech_recognition as sr
import os
import time
import json
from wit import Wit as wit
import telethontry as tele
import asyncio

async def handle_message(resp):
    try:
        if "intent" not in resp['entities']:
            print("Sorry, I don't understand your intent.")
            return
        intent = resp['entities']['intent'][0]['value']
        if(intent == "get_help"):
            print("calling scdf..")
            print("contacting NOK..")

        elif(intent == "control_appliance"):
            on_off = True if resp['entities']['on_off'][0]['value'] == "on" else False
            appliance = resp['entities']['appliance'][0]['value']
            room = ""
            if "room" in resp:
                room = "in the " + resp['entities']['room'][0]['value']
            if(on_off):
                print("turning on " + appliance + room + "..")
            else:
                print("turning off " + appliance + room + "..")

        elif(intent == "call"):
            contact = resp['entities']['person'][0]['value']
            print("calling " + contact + "..")

        elif(intent == "send_message"):
            contact = resp['entities']['person'][0]['value']
            msg = resp['entities']['message_body'][0]['value']
            print("sending " + contact + " :" + msg + "..")
            await tele.send_to(contact, msg)

        elif(intent == "get_weather"):
            # get current location
            if 'datetime' in resp['entitites']:
                date = resp['entities']['datetime'][0]['value']
                print("getting weather for " + date + "..")
            else:
                print("getting weather for today..")
    except KeyError:
        print("Sorry, I could not get the information to complete the action.")


def recog_callback(r, audio):
    try:
        transcript = r.recognize_google(audio)
        print(transcript)
        os.system("say "+ repr(transcript))
        resp = interpreter.message(transcript)
        print(resp)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(handle_message(resp))

    except sr.UnknownValueError:
        print("I could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google service; {0}".format(e))
	#print("Could not request results from Wit.ai service; {0}".format(e))

def run():
    access_token = 'YQA4LN7PWPCYQDY2YYFVUFTUXKBC4LIB'
    r = sr.Recognizer()
    mic = sr.Microphone()
    interpreter = wit(access_token)

    with mic as source:
        r.adjust_for_ambient_noise(source)

    stop_listening = r.listen_in_background(mic, recog_callback)

def stop():
    stop_listening(wait_for_stop = False)
    time.sleep(1)

if __name__ == "__main__":
    access_token = 'YQA4LN7PWPCYQDY2YYFVUFTUXKBC4LIB'
    r = sr.Recognizer()
    mic = sr.Microphone()

    interpreter = wit(access_token)

    with mic as source:
        r.adjust_for_ambient_noise(source)


    stop_listening = r.listen_in_background(mic, recog_callback)

    # with tele.client as client:
    #       client.start()
    #       client.send_message(67617730,'trying chatid')
    #
    #       # requires sign in using phone number
    #       client.run_until_disconnected()
    #       print("i'm here")
    # do other things like wait for qr code

    # stop listening
    stop_listening(wait_for_stop = False)

    # cleaning up
    time.sleep(1)
