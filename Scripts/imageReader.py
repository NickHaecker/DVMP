import skimage
import os
from skimage import data, filters, io

coins = data.coins()
camera = data.camera()
patternName = "./Pattern/test.png"
pattern = io.imread(patternName)

print(pattern)
