import time

import moderngl as mg
import numpy as np
import imageio as ii


width, height = 2048, 2048


def read(path):
    with open(path, 'r') as fp:
        return fp.read()


def uniform(p, uniform):
    for n, v in uniform.items():
        if n in p:
            p[n].value = v


def serialize(path, gpu_buffer, channels):
    data = np.frombuffer(gpu_buffer.read(), dtype=np.float32)
    data = np.multiply(data, 255.0)
    data = data.reshape((height, width, channels)).astype(np.uint8)

    ii.imwrite(path, data)

start_time = time.time()

gl = mg.create_standalone_context()

out_height = gl.buffer(reserve=width * height * 1 * 4)
out_height.bind_to_storage_buffer(0)

out_normal_sobel = gl.buffer(reserve=width * height * 4 * 4)
out_normal_sobel.bind_to_storage_buffer(1)

out_normal_offset = gl.buffer(reserve=width * height * 4 * 4)
out_normal_offset.bind_to_storage_buffer(2)

cs_height = gl.compute_shader(read("./gl/height_texture_generation.comp"))
cs_normal = gl.compute_shader(read("./gl/normal_texture_generation.comp"))

uniform_data = {"u_width": width, "u_height": height}
list(map(lambda p: uniform(p, uniform_data), [cs_height, cs_normal]))

print(f"setting up compute shader took: {time.time() - start_time}s")
start_time = time.time()

gx, gy = int(width / 8), int(height / 8)
cs_height.run(gx, gy)
cs_normal.run(gx, gy)

print(f"running compute shader took: {time.time() - start_time}s")
start_time = time.time()

serialize("out_height.png", out_height, 1)

print(f"encoding height map took: {time.time() - start_time}s")
start_time = time.time()

serialize("out_normal_sobel.tga", out_normal_sobel, 4)
serialize("out_normal_offset.tga", out_normal_offset, 4)

print(f"encoding normal maps took: {time.time() - start_time}s")
