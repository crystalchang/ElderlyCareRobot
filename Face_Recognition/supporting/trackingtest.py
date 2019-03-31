import serial
ser = serial.Serial("/dev/rfcomm0", baudrate=115200, timeout=3)

def sendToMbot(msg):
    ser.write(msg.encode())
    print("Sent: "+ msg)
    return

def listenToMbot():
    print("[debugging] in ser.inwaiting")
    msg = ser.readline().decode()
    print(msg)
    print("Received: "+ str(msg))
    return



while True:
    print("depth: ")
    depth = input()
    print("angle: ")
    angle = input()
    sendToMbot("track " + str(depth) + " " + str(angle))
    listenToMbot()
