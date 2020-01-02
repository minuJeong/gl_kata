import os

import numpy as np


if not os.path.isdir("./mesh"):
    os.makedirs("./mesh")


def writebuffer(path, data):
    with open(path, "wb") as fp:
        fp.write(data)

vbpath = "./mesh/quad.vb"
ibpath = "./mesh/quad.ib"

vb = np.array([-1.0, -1.0, -1.0, +1.0, +1.0, -1.0, +1.0, +1.0], dtype=np.float32)
writebuffer(vbpath, vb)

ib = np.array([0, 1, 2, 2, 1, 3], dtype=np.int32)
writebuffer(ibpath, ib)
