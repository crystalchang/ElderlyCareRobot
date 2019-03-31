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
    
    cv2.imshow("result", image_copy)
    
    return len(faces)


#test
for i in range (0,9):
    image = cv2.imread("/home/pi/Desktop/Elderly Care Robot/test"+str(i)+".jpg")
   
    haar_time1 = time.time()
    haar_no_faces = detect_face(haar_face_cascade,image)
    haar_time_taken = time.time() - haar_time1
    
    lbp_time1 = time.time()
    lbp_no_faces = detect_face(lbp_face_cascade,image)
    lbp_time_taken = time.time() - lbp_time1
    print("####ROUND " + str(i+1))
    print("Haar scored " + str(haar_no_faces)+"/" + str(answers[i]) + "in "
          + str(haar_time_taken))
    print("LBP scored " + str(lbp_no_faces)+"/" + str(answers[i]) + "in "
          + str(lbp_time_taken))
    
    haar_score += haar_no_faces
    haar_time += haar_time_taken
    lbp_score += lbp_no_faces
    lbp_time += lbp_time_taken
    
print ("haar score = " + str(haar_score) + ", lbp score = " + str(lbp_score))
print ("haar time = " + str(haar_time) + ", lbp time = "+ str(lbp_time))

   
