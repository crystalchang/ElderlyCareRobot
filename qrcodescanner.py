from picamera import PiCamera
from picamera.array import PiRGBArray
from imutils.video import VideoStream
import imutils
import cv2
import time
import pyzbar.pyzbar as pyzbar
import numpy as np

def handle_request(req):
    import telethontry
    if req == "send message to son":
        print("sending")
    if req == "send message to daughter":
        print("sending")
    if req == "repeat message":
        print("repeating")
    if req == "get help":
        print("getting help")
    if req == "control appliance":
        print("repeating")
    if req == "get weather":
        print("repeating")
    if req == "take photo":
        print("taking photo and sending to family chat")

def main(outqueue):
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(3.0)

    while True:
        frame = vs.read()
        if frame.all() == None:
            continue
        image = imutils.resize(frame, width=500)

        qrcodes = pyzbar.decode(image)
        for qr in qrcodes:
            request = str(qr.data)[2:-1]
            print('Type: ' + qr.type + ' Data: ' + request)
            print('Polygon points: ' + str(qr.polygon))
            points = [[x,y] for x, y in qr.polygon]
            cv2.polylines(image, [np.array(points)], True, (255, 0, 255),3)
            outqueue.put(request)

        #display frame
        cv2.imshow('QR Code Scanner',image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    vs.stop()

if __name__ == '__main__':
    main()
