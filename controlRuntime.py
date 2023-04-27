import utils.initialSetup as initialSetup
import utils.arduinoAdapter as arduinoAdapter
import controller.controllerImplementation as controllerImplementation
import ballDetection.ballDetection as ballDetection
import argparse
import cv2
import os
import time
import serial
from imutils.video import VideoStream
import utils.threadedCamera as threadedCamera
import math

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())

#vs = initialSetup.initializeCameraFeed()
#vs = threadedCamera.ThreadedCamera(1)
#front camera testing
vs = cv2.VideoCapture(1,cv2.CAP_DSHOW)
vs.set(cv2.CAP_PROP_BUFFERSIZE, 2)
vs.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
vs.set(cv2.CAP_PROP_FRAME_HEIGHT, 270)

# getInitialTableDimensions
if not os.path.isfile("assets/image.jpg"):
    time.sleep(10)
    _, frame = vs.read()
    cv2.imwrite("assets/image.jpg", frame)
    print("Image saved successfully")
#dimensions = initialSetup.getTableDimensionsHSVBound()
dimensions = {}
dimensions['xCenter'] = 150
dimensions['yCenter'] = 160
dimensions['xLow'] = 21
dimensions['xHigh'] = 296
dimensions['yLow'] = 250
dimensions['yHigh'] = 33

currStateX = 0
currStateY = 0
#video stream loop
# Open the arduino serial port
ser = serial.Serial("COM7", 9600)
time.sleep(3)
while True:
    start_time = time.time()
    frame, displacementX, displacementY = ballDetection.ballDetectWithDimensions(vs, dimensions)
    print("My program took", time.time() - start_time, "to get frame & displacement.")
    normFactor = 0.1
    pxToM = 0.1/50
    #normalized displacements -> conv px to m, and then divide by 0.1.
    displacementX = displacementX * pxToM / normFactor
    displacementY = displacementY * pxToM / normFactor
    #print(displacementX, displacementY)
    #convert from px to m, and normalize
    controlEffortX = [[0]]
    controlEffortY = [[0]]
    if displacementX:
        currStateX, controlEffortX = controllerImplementation.feedbackLoop(currStateX, displacementX)
    if displacementY:
        currStateY, controlEffortY = controllerImplementation.feedbackLoop(currStateY, displacementY)
    #fully unnormalize this is good!
    print(controlEffortX)
    controlEffortX = controlEffortX[0][0]*6/math.pi
    controlEffortY = controlEffortY[0][0]*3.5*10*6/math.pi
    arduinoAdapter.sendCommandToArduino(ser, -controlEffortX*180/math.pi, controlEffortY)
    print("My program took", time.time() - start_time, "to actuate.")
	# show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
	vs.stop()
# otherwise, release the camera
else:
	vs.release()
# close all windows
cv2.destroyAllWindows()
ser.close()