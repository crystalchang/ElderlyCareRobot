import speech_recognition as sr
import os
import time
import json
from wit import Wit as wit


access_token = 'YQA4LN7PWPCYQDY2YYFVUFTUXKBC4LIB'
r = sr.Recognizer()
mic = sr.Microphone()

interpreter = wit(access_token)

def handle_message(resp):
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
            contact = resp['entities']['contact'][0]['value']
            print("calling " + contact + "..")

        elif(intent == "send_message"):
            contact = resp['entities']['contact'][0]['value']
            msg = resp['entities']['message_body'][0]['value']
            print("sending " + contact + " :" + msg + "..")

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
	#transcript = r.recognize_wit(audio, key=access_token)
        print(transcript)
        os.system("say "+ repr(transcript))
        resp = interpreter.message(transcript)
        print(resp)
        handle_message(resp)

    except sr.UnknownValueError:
        print("I could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google service; {0}".format(e))
	#print("Could not request results from Wit.ai service; {0}".format(e))

with mic as source:
    r.adjust_for_ambient_noise(source)

stop_listening = r.listen_in_background(mic, recog_callback)

# do other things like wait for qr code
for i in range(50):
    time.sleep(1)
    print("busy...")

# stop listening
stop_listening(wait_for_stop = False)

# cleaning up
time.sleep(1)
