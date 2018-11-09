import serial
import time

port = "/dev/rfcomm0"

ser = serial.Serial(port,115200)
ser.flushInput()
curr = 10

def receivefromArduino():
    msg = ser.readline().decode()
    return msg
    

def sendtoArduino(n):
    ser.write(n.encode())
    time.sleep(5)
    
    
while True:
    sendtoArduino("sending message, do you receive?")
    time.sleep(5)
    msg = receivefromArduino()
    if (msg):
        print(msg)
    
    
