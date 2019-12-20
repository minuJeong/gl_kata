import os

import numpy as np


def write(path, mode, data):
    dirname = os.path.dirname(path)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    with open(path, mode) as fp:
        fp.write(data)

vertices = []
for x in (-1, 1):
    for y in (-1, 1):
        vertices.extend([x, y])
vertices = np.array(vertices, dtype=np.float32)
write("./mesh/quad.vb", "wb", vertices)

indices = [0, 1, 2, 2, 1, 3]
indices = np.array(indices, dtype=np.int32)
write("./mesh/quad.ib", "wb", indices)
