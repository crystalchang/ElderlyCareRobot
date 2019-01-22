from picamera import PiCamera
from picamera.array import PiRGBArray
from imutils.video import FPS
from imutils.video import VideoStream
import face_recognition
import pickle
import imutils
import serial
import cv2
import time

################### METHODS ###################
# setting up variables
lastpos = (0,0,0,0)
screenRes = [640,480]
threshold = 0.6

def isDifferent(pos):
    global lastpos
    global screenRes
    # if change in coordinates less than 5% of screen resolution
    if ((abs(pos[0] - lastpos[0])/screenRes[0]) < 0.05):
        if ((abs(pos[1] - lastpos[1])/screenRes[1]) < 0.05):
            # do nothing
            return False
    lastpos = pos
    return True


def notCentralised(pos):
    global screenRes
    # if centre of face is within 10% of the centre of the screen
    if ((abs(pos[0] - 0.5*screenRes[0])/screenRes[0]) < 0.05):
        if ((abs(pos[1] - 0.5*screenRes[1])/screenRes[1]) < 0.05):
            # do nothing
            return False
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
    C = (0.5*screenRes[0])-x-0.5*w
    
    # send centralising commands
    msg = str(Asq) + " " + str(C)
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
    

################## Communicate with Mbot ##################
def sendToMbot(msg):
    ser.write(msg.encode())
    print("Sent: "+ msg)
    print("x: " + str(x) + " w: " + str(w))
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

# setting up bluetooth serial port
ser = serial.Serial("/dev/rfcomm0", baudrate=115200)

print("[INFO] setting up camera")

# setting up camera
vs = VideoStream(usePiCamera=True).start()

# let camera warm up
time.sleep(2.0)

# start FPS throughput estimator
fps = FPS().start()
starttime = time.time()

# using cv2 haar cascades
print("[INFO] loading haar detector and dlib encodings")
haar_face_cascade=cv2.CascadeClassifier("/home/pi/Desktop/OpenCV/face_detection/haarcascade_frontalface_default.xml")
data = pickle.loads(open("dlib_encodings.pickle", "rb").read())

# tmpFrame = 1

# capture frame by frame
while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=600)
    (h,w) = frame.shape[:2]
    # only run for 1/15 frames
    #if (tmpFrame%15 == 0):
    if (True):
        print("[INFO] processing frame")
        tmpFrame = 1
        
        image = frame
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = haar_face_cascade.detectMultiScale(gray, scaleFactor=1.1, 
		minNeighbors=5, minSize=(30, 30),
		flags=cv2.CASCADE_SCALE_IMAGE)
        
        # centroid tracking
        for (x, y, w, h) in faces:
            # x, y, w, h = coord
            #draw rectangle around face
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
            if(isDifferent((x, y, w, h)) and notCentralised((x, y, w, h))):
                centralise((x, y, w, h))
        #listenToMbot()
        
        # facial recognition
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in faces]
        names = []
        
        #use confidence value to find best match
        encodings = face_recognition.face_encodings(rgb, boxes)
        
        # match new encodings to known ones
        for encoding in encodings:
            distances = face_recognition.face_distance(data["encodings"],
                    encoding)
            name = "Unknown"
            minDist = np.amin(distances)
            confidence = 100/(1+minDist)
            #find max confidence index, return person name
            threshold = 60
            if(confidence>threshold):
                index = np.where(distances == minDist)[0][0]
                name = data["names"][index] + " "+ str(confidence)[:4] + "%"
            names.append(name)
        
        # draw rectangles and print name
        for ((top, right, bottom, left), name) in zip(boxes, names):
            # draw the predicted face name on the image
            cv2.rectangle(frame, (left, top), (right, bottom),
                    (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 255, 0), 2)
    
    tmpFrame += 1
    
    # qrcodes = zbartools...

    #display frame
    cv2.imshow('Frame',image)
    fps.update()

    if ((cv2.waitKey(1) & 0xFF) == ord("q")):
        break
    if (time.time() - starttime > 70):
        break
    

fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx FPS: {:.2f}".format(fps.fps()))

cv2.destroyAllWindows()
vs.stop()







