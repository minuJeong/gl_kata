import os
import numpy as np


def write(path, mode, data):
    dirname = os.path.dirname(path)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    with open(path, mode) as fp:
        fp.write(data)


def build():
    vertices = np.zeros((4, 8), dtype=np.float32)
    vertices[0] = [-1.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
    vertices[1] = [+1.0, -1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0]
    vertices[2] = [-1.0, +1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0]
    vertices[3] = [+1.0, +1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0]
    write("./mesh/quad.vb", "wb", vertices)

    indices = np.zeros((6), dtype=np.int32)
    indices[:] = [0, 1, 2, 2, 1, 3]
    write("./mesh/quad.ib", "wb", indices)


if __name__ == "__main__":
    build()
