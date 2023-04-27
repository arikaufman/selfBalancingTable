from pySerialTransfer import pySerialTransfer as transfer
import time
import serial
import math

def send_float_to_arduino(ser, value):
    ser.write((str(value) + "\n").encode())
    #print(str(value))
    # Wait for a response from the Arduino
    response = ser.readline().strip()
    print(response)

def sendCommandToArduino(ser, controlEffortX, controlEffortY):
    controlEffortX = str(int(controlEffortX))
    controlEffortY = str(int(controlEffortY))

    while len(controlEffortX) < 3:
        controlEffortX += " "
    while len(controlEffortY) < 3:
        controlEffortY += " "

    formatString = controlEffortX
    #print(formatString)
    ser.write((formatString + "\n").encode())
    # Wait for a response from the Arduino
    response = ser.readline()
    #print(response)

#print("HERE")
ser = serial.Serial("COM7", 9600)
time.sleep(3)
counter = 0
for i in range(0,1000):
    for j in range(0,40):
        if i % 2 == 0:
            sendCommandToArduino(ser,j,-j)
        else:
            sendCommandToArduino(ser,-j,j)
        counter += 1
        print(counter)
