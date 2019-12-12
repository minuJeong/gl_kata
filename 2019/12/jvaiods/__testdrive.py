import imageio as ii
import numpy as np


norm = ii.imread("./normalmap.png").astype(np.ubyte)
roug = ii.imread("./roughness.png").astype(np.ubyte)
lumi = ii.imread("./luminosity.png").astype(np.ubyte)

img = np.zeros((512, 512, 4), dtype=np.ubyte)
img[:, :, 0:2] = norm[:, :, 0:2]
img[:, :, 2] = roug[:, :, 0]
img[:, :, 3] = lumi[:, :, 0]

# img = np.multiply(img, 255.0)
# img = img.astype(np.uint8)

ii.imwrite("combined.png", img)
