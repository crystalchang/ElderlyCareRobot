from picamera import PiCamera
from picamera.array import PiRGBArray
from imutils.video import VideoStream
import imutils
import serial
import cv2
import time

def listenToMbot():
    if (ser.inWaiting()> 0):
        msg = ser.readline().decode()
        print(msg)
        print("Sonar Distance: "+ str(msg))
        

ser = serial.Serial("/dev/rfcomm0", baudrate=115200)

print("[INFO] setting up camera")
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
haar_face_cascade=cv2.CascadeClassifier("/home/pi/Desktop/OpenCV/face_detection/haarcascade_frontalface_default.xml")

# capture frame
while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=600)
    (h,w) = frame.shape[:2]
    image = frame
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # detect face, return coords
    faces = haar_face_cascade.detectMultiScale(gray,1.1,5)
    
    for (x, y, w, h) in faces:
        # x, y, w, h = coord
        #draw rectangle around face
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # print coords, print serial dist
        print("w: " + str(w))
        print("h: " + str(h))
        listenToMbot()
    
    cv2.imshow('Frame',image)
    #clear stream in preparation for the next frame
    #rawCapture.truncate(0)

    if ((cv2.waitKey(1) & 0xFF) == ord("q")):
        break
    

cv2.destroyAllWindows()
vs.stop()


