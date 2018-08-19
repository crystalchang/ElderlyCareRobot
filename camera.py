from picamera import PiCamera
from picamera.array import PiRGBArray
#import sys
#sys.path.append('/usr/local/lib/python3.4/site-packages')
import cv2
import time

camera = PiCamera()
camera.resolution = (640,480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640,480))

time.sleep(0.1)

haar_face_cascade=cv2.CascadeClassifier("/home/pi/opencv-3.4.1/data/haarcascades/haarcascade_frontalface_alt.xml")


#capture frame by frame
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = haar_face_cascade.detectMultiScale(gray,1.1,5)

    #draw rectangle around face
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

    #display frame
    cv2.imshow('Frame',image)
    #clear stream in preparation for the next frame
    rawCapture.truncate(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    


##cascPath = sys.argv[1]
##
##camera=PiCamera()
##
##camera.start_preview()
##sleep(10)
##camera.stop_preview()
