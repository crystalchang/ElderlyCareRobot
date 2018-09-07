from picamera import PiCamera
from picamera.array import PiRGBArray
#import sys
#sys.path.append('/usr/local/lib/python3.4/site-packages')
import cv2
import time

#setup
haar_face_cascade=cv2.CascadeClassifier("/home/pi/opencv-3.4.1/data/haarcascades/haarcascade_frontalface_alt.xml")
lbp_face_cascade=cv2.CascadeClassifier("/home/pi/opencv-3.4.1/data/lbpcascades/lbpcascade_frontalface.xml")

answers = [5, 9, 6, 5, 4, 2, 4, 2, 1, 1]
haar_score = 0
lbp_score = 0
haar_time = 0
lbp_time = 0

def detect_face(cascade, image):
    image_copy = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray,1.1,5)

    #draw rectangle around face
    for (x, y, w, h) in faces:
       cv2.rectangle(image_copy, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    
    return image_copy


#test

image = cv2.imread("/home/pi/Desktop/Elderly Care Robot/test7.jpg")

haar_time1 = time.time()
haar_faces = detect_face(haar_face_cascade,image)
haar_time = time.time() - haar_time1

lbp_time1 = time.time()
lbp_faces = detect_face(lbp_face_cascade,image)
lbp_time = time.time() - lbp_time1

print("haar "+ str(haar_time) + " lbp "+ str(lbp_time))
#print("haar "+ str(haar_faces) + " lbp "+ str(lbp_faces))


cv2.imshow("haar", haar_faces)
cv2.imshow("lbp", lbp_faces)
cv2.waitKey(0)
cv2.destroyAllWindows()

