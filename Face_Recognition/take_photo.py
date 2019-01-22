import imutils
import time
import cv2
import os
from imutils.video import VideoStream

person = "Crystal"
detector=cv2.CascadeClassifier("/home/pi/Desktop/OpenCV/face_detection/haarcascade_frontalface_default.xml")
output = "/home/pi/ElderlyCareRobot/Face_Recognition/Dataset/Crystal/"

print("[INFO] starting video stream...")
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
total=0

while True:
    frame = vs.read()
    orig=frame.copy()
    frame=imutils.resize(frame,width=400)
    
    faces = detector.detectMultiScale(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),
                                      scaleFactor=1.1, minNeighbors=5,minSize=(30,30))
    
    for (x,y,w,h) in faces:
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
    
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord("k"):
        p = output+str(total)+".png"
        cv2.imwrite(p,orig)
        total += 1
        
    elif key == ord("q"):
        break

print("[INFO] {} face images stored".format(total))
print("[INFO] cleaning up")
cv2.destroyAllWindows()
vs.stop()