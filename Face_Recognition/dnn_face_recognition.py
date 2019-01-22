from imutils.video import VideoStream
import imutils
import time
import numpy as np
import argparse
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image",
                required = True, help="path to input image")
ap.add_argument("-p", "--prototxt",
                required = True, help="path to Caffe deploy prototxt file")
ap.add_argument("-m", "--model",
                required = True, help="path to Caffe pretrained model")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
                help="min probability to filter weak detections")
args = vars(ap.parse_args())

# load serialised model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

#initialise video stream and camera warm up
print("[INFO] starting video stream")
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

while True:
    # grab frame from video stream and resize
    frame = vs.read()
    frame = imutils.resize(frame,width=400)
    
    # grab frame dimensions and convert to blob
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                 1.0, (300, 300), (104.0, 177.0, 123.0))
    
    #pass blob through network and obtain detections and predictions
    net.setInput(blob)
    detections = net.forward



