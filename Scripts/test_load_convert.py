import cv2
import numpy as np
from colormap import rgb2hex

#load in picture
img = cv2.imread("Pattern/Pattern.png")
# height = 200
# width = 200

scale_percent = 120 # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)

resized = cv2.resize(img, (width, height))

print(width)
print(height)

#display picture preview
cv2.imshow("pattern", img)
cv2.waitKey(0)



#Umwandlung BGR Wert des Bildes in Hex Code

for x in range (0,width,1):
    for y in range(0,height,1):
        color = resized[y,x]
        print(color)

green = (0, 255, 0)
darkGreen = (39, 255, 95)
brown = (59, 86, 143)
blue = (255, 0, 0)

#convert to hex
rgb2hex(green)
'##008040'
print(green)
