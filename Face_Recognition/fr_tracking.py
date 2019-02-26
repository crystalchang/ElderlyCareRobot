from picamera import PiCamera
from picamera.array import PiRGBArray
from imutils.video import FPS
from imutils.video import VideoStream
import numpy as np
import face_recognition
import pickle
import imutils
import serial
import cv2
import time
import math

################### METHODS ###################

def isDifferent(pos):
    global lastpos, screenRes
    # if centroid change less than 5% of screen resolution
    lastcentroid = (lastpos[0]+0.5*lastpos[2], lastpos[1]+0.5*lastpos[3])
    poscentroid = (pos[0]+0.5*pos[2], pos[1]+0.5*pos[3])
    centroidDist = ((lastcentroid[0]-poscentroid[0])**2 + (lastcentroid[1]-poscentroid[1])**2)**0.5
    screenDiag = (screenRes[0]**2 + screenRes[1]**2)**0.5
    
    if (centroidDist/screenDiag < 0.05):
        print(" centroid/ screendiag" + str(centroid/screenDiag) + " not different")
        return False
    else:
        lastpos = pos
        print(" centroid/ screendiag" + str(centroid/screenDiag) + " different")
        return True


def notCentralised(pos):
    global screenRes
    # if centre of face is within 10% of the centre of the screen
    print("post: " + str(pos))
    limit = (screenRes[0]**2 + screenRed[1]**2)**0.5 * 0.1
    posCentroid = (pos[0]+0.5*pos[2], pos[1]+0.5*pos[3])
    disFromCentre = ((posCentroid[0]-screenRes[0])**2 + (posCentroid[1]-screenRes[1])**2)**0.5
    if (disFromCentre < limit):
        print("centralised")
        return False
    else:
        print("not centralised")
        return True

def centralise(pos):
    global screenRes
    # calculate Asq and C
    # send Asq and C, B is sonar
    x = pos[0]
    y = pos[1]
    w = pos[2]
    h = pos[3]
    Asq = (y + (0.5*h))**2
    C = x + 0.5*w - (0.5*screenRes[0])
    B = 11935 * (w**(-1.068))
    
    angle = math.atan2(C, (Asq+B**2)**0.5) * (180/3.141592)
    if (B < 40 or B > 50):
        depth = B - 45
        depth = str(depth)[:3]
    else:
        depth = "0"
    
    # send centralising commands "track depth angle"
    msg = "track " + depth + " " + str(angle)[:2]
    sendToMbot(msg)
    

def giveInstructions(pos):
    x = pos[0]
    y = pos[1]
    w = pos[2]
    h = pos[3]
    # left and right edge
    if (x < 125):
        msg += " counter"
    elif (x + w > 515):
        msg += " clock"
    # size of size
    if (w < 180):
        msg += " forward"
    elif (w > 250):
        msg += " back"
    sendToMbot(msg)
    
def faceDetection(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    return haar_face_cascade.detectMultiScale(gray, scaleFactor=1.1, 
            minNeighbors=5, minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE)

def faceRecognition(image, faces):
    global data, threshold
    
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in faces]
    names = []
    
    #use confidence value to find best match
    encodings = face_recognition.face_encodings(rgb, boxes)
        
    # match found faces' encodings to known ones
    for encoding in encodings:
        distances = face_recognition.face_distance(data["encodings"],
                encoding)
        name = "Unknown"
        minDist = np.amin(distances)
        confidence = 100/(1+minDist)
        #find max confidence index, return person name
        if(confidence>threshold):
            index = np.where(distances == minDist)[0][0]
            name = data["names"][index] + " "+ str(confidence)[:4] + "%"
        names.append(name)
    return zip(boxes, names)
  
################## Communicate with Mbot ##################
def sendToMbot(msg):
    ser.write(msg.encode())
    print("Sent: "+ msg)
    # print("x: " + str(x) + " w: " + str(w))
    # need to sleep
    time.sleep(2)
    
def listenToMbot():
    if (ser.inWaiting()> 0):
        print("[debugging] in ser.inwaiting")
        msg = ser.readline().decode()
        print(msg)
        print("Received: "+ str(msg))
        
        
#####################################################
##################   MAIN()   #######################
#####################################################
        
def tracking(user):
    global fps, lastpos, screenRes, threshold, ser, vs, haar_face_cascade, data
    
    # user = ((x, y, w, h), name)
    print("start tracking")
    print(user)
    user_box = user[0]
    name = user[1]
    print(user_box)
    
    n = -1
    
    while True:
        # grab next frame
        frame = vs.read()
        frame = imutils.resize(frame, width=500)
        (h,w) = frame.shape[:2]
        # print("[INFO] processing frame")
        # image = frame
        faces = faceDetection(frame)
        
        # every nth frame, check if user still in frame
        if n == 9:
            userMissing = True
            if faces.any():
                recognised_faces = faceRecognition(frame, faces)
                for ((top, right, bottom, left), name) in recognised_faces:
                    if (name != "Unknown"):
                        userMissing = False
                        user_box = (left, top, right-left, top-bottom) #(x,y,w,h)
                    # draw the predicted face name on the image
                    cv2.rectangle(frame, (left, top), (right, bottom),
                            (0, 255, 0), 2)
                    y = top - 15 if top - 15 > 15 else top + 15
                    cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                            0.75, (0, 255, 0), 2)
        
        else: # n > 0
            
            # find face closest to last face
            userMissing = False
            centroidDist = []
            # user_box == (x,y,w,h)
            user_centroid = (user_box[0]+(0.5*user_box[2]),user_box[1]+(0.5*user_box[3]))
            print("user_centroid:")
            print(user_centroid)
            
            for (x, y, w, h) in faces:
                centroid = (x+(0.5*w),y+(0.5*h))                
                xDiff = abs(user_centroid[0]-centroid[0])
                yDiff = abs(user_centroid[1]-centroid[1])
                centroidDist.append((xDiff**2 + yDiff**2)**0.5)
                
            print("centroidDist: ")
            print(centroidDist)
            
            if (min(centroidDist)>100):
                userMissing = True
            index = centroidDist.index(min(centroidDist))
            # follow the closest one
            user_box = faces[index]
            
            # draw rectangles
            i = 0
            for (x,y,w,h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h),
                            (0, 255, 0), 2)
                y = y - 15 if y - 15 > 15 else y + 15
                if(i == index):
                    cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                            0.75, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, "Unknown", (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                            0.75, (0, 255, 0), 2)
                i += 1
            
        # show frame
        cv2.imshow('Frame',frame)
        key = cv2.waitKey(0) & 0xFF
        if key == ord("q"):
            break
        fps.update()
    
        if userMissing:
            return
        
        # increment one frame
        n = (n+1)%10
        
        # track user
        if(isDifferent(user_box) and notCentralised(user_box)):
            print("centralising")
            centralise(user_box)
    
    cv2.destroyAllWindows()
    vs.stop()
    
def findUser():
    global fps, lastpos, screenRes, threshold, ser, vs, haar_face_cascade, data
    doTracking = False
    # send to mbot msg to trigger rotate until sonar sequence
    sendToMbot("find")
    # continuously scan for face detections
    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=500)
        (h,w) = frame.shape[:2]
        # print("[INFO] processing frame")
        #image = frame
        
        faces = faceDetection(frame)
        
        if faces.any():
            print("face detected")
            print(faces)
            # get names of faces
            recognised_faces = faceRecognition(frame, faces)
            # check if face is user's
            for ((top, right, bottom, left), name) in recognised_faces:
                print(name)
                if ("Unknown" not in name):
                    doTracking = True
                    user_coord = ((top, right, bottom, left), name)
                    lastpos = (left, top, right-left, bottom-top)
                # draw the predicted face name on the image
                cv2.rectangle(frame, (left, top), (right, bottom),
                        (0, 255, 0), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, (0, 255, 0), 2)
        cv2.imshow('Frame',frame)
        key = cv2.waitKey(0) & 0xFF
        if key == ord("q"):
            break
        
        fps.update()
        listenToMbot()
        if doTracking:
            # sendToMbot("stopFind")
            print("do tracking")
            return (lastpos,name)
        else:
            sendToMbot("find")
    cv2.destroyAllWindows()
    vs.stop()
    
if __name__ == "__main__":
    
    ################ SETUP #################
    # setting up variables
    screenRes = [500,375]
    lastpos = (0,0,0,0)
    threshold = 0.6

    # setting up bluetooth serial port
    ser = serial.Serial("/dev/rfcomm0", baudrate=115200)

    print("[INFO] setting up camera")

    # setting up camera
    vs = VideoStream(usePiCamera=True).start()

    # let camera warm up
    time.sleep(2.0)

    print("[INFO] loading haar detector and dlib encodings")
    haar_face_cascade=cv2.CascadeClassifier("/home/pi/Desktop/OpenCV/face_detection/haarcascade_frontalface_default.xml")
    data = pickle.loads(open("dlib_encodings.pickle", "rb").read())

    # start FPS throughput estimator
    fps = FPS().start()
    starttime = time.time()
    
    #global fps, vs

    while True:
        user = findUser()
        tracking(user)
        # if exit command, break
    
    # exiting
    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx FPS: {:.2f}".format(fps.fps()))
    
    
    
    
