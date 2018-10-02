from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2
import time
import zbar
import numpy as np

camera = PiCamera()
camera.resolution = (640,480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640,480))

time.sleep(0.1)


#capture frame by frame
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = cv2.imread(frame, 1)
    
    scanner = zbar.Scanner()
    qrcodes = scanner.scan(image)
    for qr in qrcodes:
        print('Type: ' + qr.type + ' Data: ' + str(qr.data))
        print('Polygon points: ' + str(qr.polygon))
        points = [[x,y] for x, y in qr.polygon]
        cv2.polylines(image, [np.array(points)], True, (255, 0, 255),3)
        

    #display frame
    cv2.imshow('Frame',image)
    #clear stream in preparation for the next frame
    rawCapture.truncate(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

