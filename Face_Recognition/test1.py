#compare each photo with each other
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import numpy as np

data = pickle.loads(open("dlib_encodings.pickle", "rb").read())
print(data["names"])

for i in range(0,len(data["encodings"])):
    confidences = face_recognition.face_distance(data["encodings"], data["encodings"][i])
    conf = []
    for c in confidences:
        conf.append(100/(1+c))
    print(data["names"][i])
    print(conf)