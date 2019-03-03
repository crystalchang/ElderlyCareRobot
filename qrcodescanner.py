from picamera import PiCamera
from picamera.array import PiRGBArray
from imutils.video import VideoStream
import imutils
import cv2
import time
import pyzbar.pyzbar as pyzbar
import numpy as np

vs = VideoStream(usePiCamera=True).start()
time.sleep(3.0)

while True:
    frame = vs.read()
    if not frame:
        continue
    frame = imutils.resize(frame, width=400)
    (h,w) = frame.shape[:2]

# camera = PiCamera()
# camera.resolution = (640,480)
# camera.framerate = 32
# rawCapture = PiRGBArray(camera, size=(640,480))
#
# time.sleep(0.1)
# print("starting qrcodescanner")
#
#
# #capture frame by frame
# for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
#     image = frame.array

    qrcodes = pyzbar.decode(image)
    print("finding qrcodes")
    print(qrcodes)
    for qr in qrcodes:
        print('Type: ' + qr.type + ' Data: ' + str(qr.data))
        print('Polygon points: ' + str(qr.polygon))
        points = [[x,y] for x, y in qr.polygon]
        cv2.polylines(image, [np.array(points)], True, (255, 0, 255),3)


    #display frame
    cv2.imshow('QR Code Scanner',image)
    #clear stream in preparation for the next frame
    rawCapture.truncate(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
vs.stop()
