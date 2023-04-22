import utils.initialSetup as initialSetup
import controller.controllerImplementation as controllerImplementation
import ballDetection.ballDetection as ballDetection
import argparse
import cv2
import os
from imutils.video import VideoStream

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())

#vs = initialSetup.initializeCameraFeed()
#front camera testing
vs = VideoStream(src=0).start()

# getInitialTableDimensions
if not os.path.isfile("assets/image.jpg"):
    cv2.imwrite("assets/image.jpg", vs.read())
    print("Image saved successfully")
dimensions = initialSetup.getTableDimensions()

currState = 0
#video stream loop
while True:
    frame, displacementX, displacementY = ballDetection.ballDetectWithDimensions(vs, dimensions['xCenter'], dimensions['yCenter'])
    print(displacementX, displacementY)
    if displacementX or displacementY:
        currState, controlEffort = controllerImplementation.feedbackLoop(currState, displacementX)
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