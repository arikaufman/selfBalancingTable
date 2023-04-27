import cv2
import numpy as np

# convert BGR color to HSV color
bgr_color = np.uint8([[[254, 251, 254]]])
hsv_color = cv2.cvtColor(bgr_color, cv2.COLOR_BGR2HSV)

# define lower and upper bounds for HSV color
lower_hsv = np.array([hsv_color[0][0][0]-3, 50, 50])
upper_hsv = np.array([hsv_color[0][0][0]+3, 255, 255])

# print results
print("Lower HSV bound:", lower_hsv)
print("Upper HSV bound:", upper_hsv)
