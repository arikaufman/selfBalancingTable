from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import os

def getTableDimensions():
	# Load image
	dimensions = {}
	img = cv2.imread('assets/image.jpg')
	# Convert image to grayscale and mask
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
	cv2.imshow('Mask', thresh)
	# Find contours in binary image
	contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# Loop over contours to find the rectangle
	for contour in contours:
		# Approximate contour to polygon
		approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
		# Check if polygon has four corners
		if len(approx) == 4 and cv2.contourArea(contour) > 250:
			# Calculate moments of contour
			M = cv2.moments(contour)
			# Check if polygon is convex
			if cv2.isContourConvex(approx):
				# Draw contour on original image
				cv2.drawContours(img, [approx], 0, (0, 255, 0), 2)
				# Calculate centroid of contour and draw circle, set perspective distortion factor (due to camera tilt)
				perspectiveDistFactor = 0.95 
				cx = int(M['m10'] / M['m00'])
				cy = int(perspectiveDistFactor*M['m01'] / M['m00'])
				cv2.circle(img, (cx, cy), 5, (0, 0, 255), -1)
				dimensions['xCenter'] = cx
				dimensions['yCenter'] = cy
				dimensions['xLow'] = approx[2][0][0]
				dimensions['xHigh'] = approx[0][0][0]
				dimensions['yLow'] = approx[2][0][1]
				dimensions['yHigh'] = approx[0][0][1]
				cv2.circle(img, (dimensions['xLow'], dimensions['yLow']), 5, (0, 0, 255), -1)
				cv2.circle(img, (dimensions['xHigh'], dimensions['yHigh']), 5, (255, 0, 0), -1)
	print(dimensions)
	# Save image with bounding box
	cv2.imwrite('assets/output.jpg', img)
	cv2.waitKey()
	cv2.destroyAllWindows()
	return dimensions

def getTableDimensionsHSVBound():
	# Load image
	dimensions = {}
	whiteLower = (0,0,240)
	whiteUpper = (180,20,255)
	#whiteLower = (147,50,50)
	#whiteUpper = (153,255,255)
	img = cv2.imread('assets/image.jpg')
	#blurred = cv2.GaussianBlur(img, (11, 11), 0)
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "orange", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, whiteLower, whiteUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	cv2.imshow('Mask', mask)
	# Find contours in binary image
	contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	for contour in contours:
		#taxe max contour
		approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(max(contours), True), True)
		#approx = max(contours)
		# Calculate moments of contour
		M = cv2.moments(max(contours))
		# Check if polygon is convex
		if cv2.isContourConvex(approx):
			# Draw contour on original image
			cv2.drawContours(img, [approx], 0, (0, 255, 0), 2)
			# Calculate centroid of contour and draw circle, set perspective distortion factor (due to camera tilt)
			perspectiveDistFactor = 0.95 
			cx = int(M['m10'] / M['m00'])
			cy = int(perspectiveDistFactor*M['m01'] / M['m00'])
			cv2.circle(img, (cx, cy), 5, (0, 0, 255), -1)
			dimensions['xCenter'] = cx
			dimensions['yCenter'] = cy
			dimensions['xLow'] = approx[2][0][0]
			dimensions['xHigh'] = approx[0][0][0]
			dimensions['yLow'] = approx[2][0][1]
			dimensions['yHigh'] = approx[0][0][1]
			cv2.circle(img, (dimensions['xLow'], dimensions['yLow']), 5, (0, 0, 255), -1)
			cv2.circle(img, (dimensions['xHigh'], dimensions['yHigh']), 5, (255, 0, 0), -1)
	print(dimensions)
	# Save image with bounding box
	cv2.imwrite('assets/output.jpg', img)
	cv2.waitKey()
	cv2.destroyAllWindows()
	return dimensions

def initializeCameraFeed():
	## Get all available video devices
	devices = []
	for i in range(10):
		cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
		if cap.isOpened():
			devices.append(i)
		cap.release()

	# Print the list of available devices
	print("Available streaming devices:" , devices)

	if len(devices) > 1:
		# Start the video stream from the USB camera, and allow warmup
		vs = VideoStream(src=1).start()
		time.sleep(2.0)
		print("camera connection successful")
		return vs
	else:
		raise Exception("USB Camera not connected.")

#getTableDimensions()