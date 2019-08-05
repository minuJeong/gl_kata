import os

import moderngl as mg
import numpy as np
import imageio as ii


def read(path):
    with open(path, "r") as fp:
        return fp.read()


def uniform(p, n, v):
    if not p:
        return

    if n in p:
        p[n].value = v


def get_next_name():
    template = "output_{}.png"
    dst_name = template.format(0)
    i = 1
    while os.path.isfile(dst_name):
        dst_name = template.format(i)
        i += 1
    return dst_name

w, h = 512, 512
gx, gy = int(w / 8), int(h / 8)

gl = mg.create_standalone_context()

dat_0 = gl.buffer(reserve=w * h * 4 * 4)
dat_0.bind_to_storage_buffer(0)

cs = gl.compute_shader(read("./gl/compute.glsl"))

uniform(cs, "u_wh", (w, h))

cs.run(gx, gy)

data = np.frombuffer(dat_0.read(), dtype=np.float32)
data = data.reshape((h, w, 4))
data = data[::-1]
data = np.multiply(data, 255.0)
data = data.astype(np.uint8)

ii.imwrite(get_next_name(), data)
