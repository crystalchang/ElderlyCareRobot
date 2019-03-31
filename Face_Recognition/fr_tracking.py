from picamera import PiCamera
from picamera.array import PiRGBArray
# from imutils.video import FPS
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

def centralise(pos):
    global screenRes
    # calculate Asq and C
    # send Asq and C, B is depth
    x = pos[0]
    y = pos[1]
    w = pos[2]
    h = pos[3]
    Asq = (y + (0.5*h))**2
    C = x + 0.5*w - (0.5*screenRes[0])
    B = 11935 * (w**(-1.068))

    angle = math.atan2(C, (Asq+B**2)**0.5) * (180/3.141592)
    print("x: " + str(x) + " w: " + str(w) + " C: " + str(C))
    angle = angle * 0.6
    print(angle)
    if abs(angle) < 5:
        angle = "0"
    else:
        angle = str(angle)[:str(angle).find(".")]

    if (B < 35 or B > 55):
        depth = B - 45
        depth = str(depth)[:str(depth).find(".")]
    else:
        depth = "0"

    # send centralising commands "track depth angle"
    msg = "track " + depth + " " + angle
    if (msg != "track 0 0"):
        sendToMbot(msg)
        time.sleep(0.3)
    else:
        print("already centralised")
    listenToMbot()

def findClosestFace(faces, user_box):
    centroidDist = []
    user_centroid = (user_box[0]+(0.5*user_box[2]),user_box[1]+(0.5*user_box[3]))

    for (x, y, w, h) in faces:
        centroid = (x+(0.5*w),y+(0.5*h))
        xDiff = abs(user_centroid[0]-centroid[0])
        yDiff = abs(user_centroid[1]-centroid[1])
        centroidDist.append((xDiff**2 + yDiff**2)**0.5)

    print("centroidDist: " + str(centroidDist))
    if (min(centroidDist)>100):
        return False
    index = centroidDist.index(min(centroidDist))
    return tuple(faces[index])

def faceDetection(image):
    global haar_face_cascade
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
    global ser
    ser.write(msg.encode())
    print("Sent: "+ msg)
    return

def listenToMbot():
    print(2.1)
    global ser
    print("[debugging] in ser.inwaiting")
    msg = ser.readline().decode()
    print(msg)
    print("Received: "+ str(msg))
    return


#####################################################
##################   MAIN()   #######################
#####################################################

def tracking(user, vs):
    # user = ((x, y, w, h), name)
    user_box = user[0]
    name = user[1]

    n = -1
    while True:
        # grab next frame
        frame = vs.read()
        frame = imutils.resize(frame, width=600)
        (h,w) = frame.shape[:2]

        faces = faceDetection(frame)
        if faces != ():
            # every nth frame, perform faceRecognition
            if n == 9:
                userMissing = True
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
            else: # other 9 frames
                userMissing = False
                if(n != -1): # find face closest to last face
                    closest = findClosestFace(faces, user_box)
                    if type(closest) == type(False):
                        userMissing = True
                    else:
                        user_box = closest
                # draw rectangles
                for (x,y,w,h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h),
                                (0, 255, 0), 2)
                    y = y - 15 if y - 15 > 15 else y + 15
                    face = (x,y,w,h)
                    if ((x,y,w,h) == user_box):
                        cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                                0.75, (0, 255, 0), 2)
                    else:
                        cv2.putText(frame, "Unknown", (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                                0.75, (0, 255, 0), 2)
        else:
            userMissing = True
        cv2.imshow('Frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        #fps.update()
        if userMissing:
            return
        else:
            # increment one frame
            n = (n+1)%10
            # track user
            if(n%3 == 0):
                centralise(user_box)

    cv2.destroyAllWindows()
    vs.stop()

def findUser(vs):
    global lastpos
    doTracking = False
    # send to mbot msg to trigger rotate until sonar sequence
    sendToMbot("find")
    # continuously scan for face detections
    while True:
        time.sleep(1.0)
        frame = vs.read()
        frame = imutils.resize(frame, width=600)
        (h,w) = frame.shape[:2]

        faces = faceDetection(frame)
        print(faces)

        if (faces != ()):
            print("face detected")
            print(faces)
            # get names of faces
            recognised_faces = faceRecognition(frame, faces)
            # check if face is user's
            for ((top, right, bottom, left), name) in recognised_faces:
                if ("known" not in name):
                    doTracking = True
                    # user_coord = ((top, right, bottom, left), name)
                    username = name
                    lastpos = (left, top, right-left, bottom-top)
                # draw the predicted face name on the image
                cv2.rectangle(frame, (left, top), (right, bottom),
                        (0, 255, 0), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, (0, 255, 0), 2)
        cv2.imshow('Frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        #fps.update()
        listenToMbot()
        if doTracking:
            return (lastpos,username)
        else:
            sendToMbot("find")
    cv2.destroyAllWindows()
    vs.stop()

if __name__ == "__main__":

    ################ SETUP #################
    # setting up variables
    screenRes = [600,450]
    lastpos = (0,0,0,0)
    threshold = 0.6

    # setting up bluetooth serial port
    ser = serial.Serial("/dev/rfcomm0", baudrate=115200, timeout=1)

    print("[INFO] setting up camera")

    # setting up camera
    vs = VideoStream(usePiCamera=True).start()

    # let camera warm up
    time.sleep(2.0)

    print("[INFO] loading haar detector and dlib encodings")
    haar_face_cascade=cv2.CascadeClassifier("/home/pi/Desktop/OpenCV/face_detection/haarcascade_frontalface_default.xml")
    data = pickle.loads(open("dlib_encodings.pickle", "rb").read())

    # start FPS throughput estimator
    # fps = FPS().start()

    while True:
        user = findUser(vs)
        tracking(user, vs)

    # exiting
    #fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx FPS: {:.2f}".format(fps.fps()))
