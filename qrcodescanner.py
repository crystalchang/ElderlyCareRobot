from picamera import PiCamera
from picamera.array import PiRGBArray
from imutils.video import VideoStream
import imutils
import cv2
import time

import pyzbar.pyzbar as pyzbar
import numpy as np
import webbrowser

from gtts import gTTS as gtts
from pygame import mixer

def say(stringToRead):
    #stringToRead = stringToRead.replace("''", "")
    tts = gtts(text=repr(stringToRead), lang="en")
    tts.save("tts.mp3")
    mixer.music.load("tts.mp3")
    mixer.music.play()

def take_photo(vs):
    say("okay taking photo in three")
    time.sleep(0.4)
    say("two")
    time.sleep(0.4)
    say("one")
    mixer.music.load("capture.mp3")
    mixer.music.play()
    frame = vs.read()
    p = "takephoto.png"
    cv2.imwrite(p,frame)

def handle_request(req, outqueue, vs):
    if req == "call wife":
        outqueue.put("call wife")
    elif req == "call daughter":
        outqueue.put("call daughter")
    elif req == "repeat message":
        outqueue.put("repeat")
    elif req == "get_help":
        outqueue.put("help")
    elif "on " in req:
        webbrowser.open("http://127.0.0.1:5000/service/"+req[3:])
        say("Okay, I'm turning on the " + req[3:])
    elif req == "get_weather":
        print("getting weather")
    elif "take_photo" in req:
        take_photo(vs)
        outqueue.put("photo " + req[11:])
    return

def main(queue):
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(3.0)
    lastrequest = ""

    mixer.init()
    count = 0
    while True:
        frame = vs.read()
        if frame.all() == None:
            continue
        image = imutils.resize(frame, width=500)

        qrcodes = pyzbar.decode(image)
        for qr in qrcodes:
            request = str(qr.data)[2:-1]
            #
            #print('Polygon points: ' + str(qr.polygon))
            points = [[x,y] for x, y in qr.polygon]
            cv2.polylines(image, [np.array(points)], True, (255, 0, 255),3)
            if(request != lastrequest):
                lastrequest = request
                print('Type: ' + qr.type + ' Data: ' + request)
                handle_request(lastrequest, queue, vs)
        count = (count + 1)%100
        if count == 99:
            lastrequest=""
        #display frame
        cv2.imshow('QR Code Scanner',image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    vs.stop()

if __name__ == '__main__':
    main(outqueue)
