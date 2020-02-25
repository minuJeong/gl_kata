import math

import numpy as np
import imageio as ii


np.zeros()
for i in range(100):
    angle = i * 0.2
    radius = 0.1 + i * 0.2
    x = math.cos(angle) * radius;
    y = math.sin(angle) * radius;
    

    p = (x, y)
