from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import os

#define color boundaries of ball we want to try. Currently set to orange.
orangeLower = (13, 100, 100)
orangeUpper = (33, 255, 255)

#orangeLower = (14, 20, 180)
#orangeUpper = (34, 255, 255)

def ballDetectWithDimensions(vs, dimensions):
	displacementX = 0
	displacementY = 0
	# grab the current frame
	_, frame = vs.read()
	if frame is None:
		return

	# resize the frame, blur it, and convert it to the HSV
	# color space
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "orange", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, orangeLower, orangeUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = None
	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		# only proceed if the radius meets a minimum size
		if radius > 5:
			#if center[0] <= dimensions['xLow'] and center[0] >= dimensions['xHigh'] and center[1] <= dimensions['yLow'] and center[1] >= dimensions['yHigh']:
			displacementX = center[0] - dimensions['xCenter']
			displacementY = center[1] - dimensions['yCenter']
			# draw the centroid on frame
			cv2.circle(frame, center, 5, (0, 0, 255), -1)
	return frame, displacementX, displacementY
#Helpful for Testing, Deprecated in current format.
def ballDetectWithContrail(cameraID):
	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-b", "--buffer", type=int, default=64,
		help="max buffer size")
	args = vars(ap.parse_args())

	#queue of points for contrail
	pts = deque(maxlen=args["buffer"])

	# Start the video stream from the USB camera
	vs = VideoStream(src=cameraID).start()

	# allow the camera or video file to warm up
	time.sleep(2.0)
	print("success")

	counter = 0
	# keep looping
	while True:
		# grab the current frame
		frame = vs.read()
		# handle the frame from VideoCapture or VideoStream
		frame = frame[1] if args.get("video", False) else frame
		# if we are viewing a video and we did not grab a frame,
		# then we have reached the end of the video
		if frame is None:
			break

		# Save image if not saved
		if not os.path.isfile("image.jpg"):
			cv2.imwrite("image.jpg", frame)
			print("Image saved successfully")

		# resize the frame, blur it, and convert it to the HSV
		# color space
		frame = imutils.resize(frame, width=600)
		blurred = cv2.GaussianBlur(frame, (11, 11), 0)
		hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

		# construct a mask for the color "green", then perform
		# a series of dilations and erosions to remove any small
		# blobs left in the mask
		mask = cv2.inRange(hsv, orangeLower, orangeUpper)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)
		center = None
		# only proceed if at least one contour was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
			# only proceed if the radius meets a minimum size
			if radius > 5:
				# draw the circle and centroid on the frame,
				# then update the list of tracked points
				cv2.circle(frame, (int(x), int(y)), int(radius),
					(0, 255, 255), 2)
				cv2.circle(frame, center, 5, (0, 0, 255), -1)
				displacementX = center[0] - baseX
				displacementY = center[1] - baseY

				if counter % 50 == 0:
					# Print the displacement in the x and y direction
					print("Displacement X: ", displacementX)
					print("Displacement Y: ", displacementY)
				counter += 1
		# update the points queue
		pts.appendleft(center)

		# loop over the set of tracked points
		for i in range(1, len(pts)):
			# if either of the tracked points are None, ignore
			# them
			if pts[i - 1] is None or pts[i] is None:
				continue
			# otherwise, compute the thickness of the line and
			# draw the connecting lines
			thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
			cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
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
