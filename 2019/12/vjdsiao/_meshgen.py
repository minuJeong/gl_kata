import os

import numpy as np
from glm import *


def write(path, data):
    dirname = os.path.dirname(path)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    with open(path, "wb") as fp:
        fp.write(data)


def build():
    v0 = vec2(-1.0, -1.0)
    v1 = vec2(+1.0, -1.0)
    v2 = vec2(-1.0, +1.0)
    v3 = vec2(+1.0, +1.0)
    vertices = np.array([*v0, *v1, *v2, *v3], dtype=np.float32)
    write("./mesh/quad.vb", vertices.tobytes())

    indices = np.array([0, 1, 2, 2, 1, 3], dtype=np.int32)
    write("./mesh/quad.ib", indices.tobytes())


if __name__ == "__main__":
    build()
