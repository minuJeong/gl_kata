
import moderngl as mg
import numpy as np
import imageio as ii


def read(path):
    with open(path, 'r') as fp:
        return fp.read()


def set_uniforms(program, uniform_names, uniform_values):
    for n, v in zip(uniform_names, uniform_values):
        if n in program:
            program[n].value = v


lsx, lsy = 32, 32
u_widht, u_height = 512, 512
gx, gy = int(512 / lsx), int(512 / lsy)

gl = mg.create_standalone_context()

buffer_0 = gl.buffer(reserve=512 * 512 * 4 * 4)
buffer_0.bind_to_storage_buffer(0)

cs = gl.compute_shader(read("./gl/compute.glsl"))

set_uniforms(cs, ["u_width", "u_height"], [u_widht, u_height])

cs.run(gx, gy)

data_0 = np.frombuffer(buffer_0.read(), dtype=np.float32)
data_0 = data_0.reshape((u_height, u_widht, 4))
data_0 = np.multiply(255.0, data_0)
data_0 = data_0.astype(np.uint8)

ii.imwrite("output.png", data_0)
