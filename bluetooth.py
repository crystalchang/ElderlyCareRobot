import serial
import time

port = "/dev/ttyUSB1"

ser = serial.Serial(port,115200)
ser.flushInput()
curr = 10

def receivefromArduino():
    msg = ser.readline().decode()
    print("Received: " + str(msg))

def sendtoArduino(n):
    ser.write(str(n).encode())
    print(n)
    time.sleep(5)
    
    
while True:
    sendtoArduino(curr)
    time.sleep(5)
    receivefromArduino()
    curr += 10
    
