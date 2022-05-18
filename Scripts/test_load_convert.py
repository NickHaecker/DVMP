import cv2
import numpy as np
#from colormap import rgb2hex

#load in picture
img = cv2.imread("Pattern/Pattern.png")
# height = 200
# width = 200

scale_percent = 120 # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)

resizedPattern = cv2.resize(img, (width, height))

print(width)
print(height)

#display picture preview
cv2.imshow("pattern", resizedPattern)
cv2.waitKey(0)



#Umwandlung BGR Werte (CV2 macht da Faxen) des Bildes in RGB Werte

rgb_pattern = resizedPattern[:, :, ::-1]

for x in range (0,width,1):
    for y in range(0,height,1):
        color = rgb_pattern[y,x]

#Festlegen der Farben in RGB Werten
green = (0, 255, 0)
darkGreen = (53, 101, 20)
brown = (143, 86, 59)
blue = (0, 0, 255)

#Umwandlung RGB in Hex

#convert to hex
conv2hex = '#%02x%02x%02x'

conv2hexGreen = conv2hex%green
conv2hexDarkGreen = conv2hex%darkGreen
conv2hexBrown = conv2hex%brown
conv2hexBlue = conv2hex%blue

