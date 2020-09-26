import numpy as np
import imageio as ii
from glm import *


WID = 128
HEI = 64

img = np.zeros(shape=(HEI, WID, 4), dtype=np.float32)

for x in range(WID):
    for y in range(HEI):
        uv = vec2(x / WID, y / HEI)
        uv = uv * 2.0 - 1.0
        uv = abs(uv)

        d = uv.x + uv.y
        d = smoothstep(1.01, 1.0, d)

        rgba = vec4(d, d, d, d)
        img[y, x] = rgba

img = np.multiply(img, 255.0)
ii.imwrite("alpha.png", img.astype(np.uint8))
