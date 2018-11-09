import serial 
from time import sleep

ser = serial.Serial("/dev/rfcomm0", baudrate=115200)

count = 0
while count<10:
    #ser.write( str(count))
    msg= str(count)
    ser.write(msg.encode())
    msg = ser.readline().decode()
    print("Received: "+ str(msg))
    count = count+1