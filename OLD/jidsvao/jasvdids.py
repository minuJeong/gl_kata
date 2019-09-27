import moderngl as mg
import imageio as ii
import numpy as np


def read(path):
    context = None
    with open(path, 'r') as fp:
        context = fp.read()

    contents = []
    for line in context.splitlines():
        if not line.startswith("#include "):
            contents.append(line)
        else:
            contents.append(read(line.split("#include ")[1]))

    return "\n".join(contents)

gl = mg.create_standalone_context()
cs = gl.compute_shader(read("./cs.glsl"))
if "u_resolution" in cs:
    cs["u_resolution"].value = (512, 512)

buf_color = gl.buffer(reserve=512 * 512 * 4 * 4)
buf_color.bind_to_storage_buffer(0)

gx, gy = int(512 / 8), int(512 / 8)
cs.run(gx, gy)

data = np.frombuffer(buf_color.read(), dtype=np.float32)
data = np.multiply(data, 255.0)
data = data.astype(np.uint8)
data = data.reshape((512, 512, 4))
ii.imwrite("output.png", data)
