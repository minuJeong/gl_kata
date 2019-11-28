import os

import numpy as np


def write(path, data):
    dirpath = os.path.dirname(path)
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)

    with open(path, "wb") as fp:
        fp.write(data)


def _build_screen_mesh():
    vb = np.array(
        (
            # in_pos               # in_texcoord
            (-1.0, -1.0, 0.0, 1.0, 0.0, 0.0),
            (-1.0, +1.0, 0.0, 1.0, 0.0, 1.0),
            (+1.0, -1.0, 0.0, 1.0, 1.0, 0.0),
            (+1.0, +1.0, 0.0, 1.0, 1.0, 1.0),
        )
    ).flatten().astype(np.float32).tobytes()
    write("./mesh/screen_mesh.vb", vb)

    ib = np.array((0, 1, 2, 2, 1, 3)).astype(np.int32).tobytes()
    write("./mesh/screen_mesh.ib", ib)


def main():
    _build_screen_mesh()


if __name__ == "__main__":
    main()
