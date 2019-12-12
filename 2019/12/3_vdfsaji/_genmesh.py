import os
import numpy as np


def write_bytes(path, data):
    with open(path, "wb") as fp:
        fp.write(data)


def gen_quad():
    vb = (
        np.array(
            [
                [-1.0, -1.0, 0.0, 1.0,],
                [+1.0, -1.0, 0.0, 1.0,],
                [-1.0, +1.0, 0.0, 1.0,],
                [+1.0, +1.0, 0.0, 1.0,],
            ]
        )
        .astype(np.float32)
        .tobytes()
    )

    ib = np.array([0, 1, 2, 2, 1, 3]).astype(np.int32).tobytes()

    write_bytes("./mesh/quad.vb", vb)
    write_bytes("./mesh/quad.ib", ib)


if not os.path.isdir("./mesh"):
    os.makedirs("./mesh")
gen_quad()
