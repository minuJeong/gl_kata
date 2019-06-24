# NOT WORKING - SHOULD FIX SOME DAY ;(

import moderngl as mg
import numpy as np
import imageio as ii

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


u_width, u_height = 512, 512
gx, gy = int(u_width / 8), int(u_height / 8)


def read(path):
    with open(path, "r") as fp:
        return fp.read()


def set_uniform(p, n, v):
    if p and n in p:
        p[n].value = v


def render():
    gl = mg.create_standalone_context()
    print(gl.version_code)

    cs_twirl = gl.compute_shader(read("./gl/twirl.glsl"))
    cs_median = gl.compute_shader(read("./gl/median.glsl"))

    set_uniform(cs_twirl, "u_width", u_width)
    set_uniform(cs_twirl, "u_height", u_height)
    set_uniform(cs_median, "u_width", u_width)
    set_uniform(cs_median, "u_height", u_height)

    buffer_allocation = u_width * u_height * 4 * 4

    noise = np.random.uniform(0.0, 1.0, (u_height, u_width, 4))
    noise[:, :, -1] = 1.0

    data_0 = gl.buffer(reserve=buffer_allocation)
    data_1 = gl.buffer(reserve=buffer_allocation)
    data_1.bind_to_storage_buffer(1)
    data_0.bind_to_storage_buffer(0)

    noise_data = noise.astype(np.float32).tobytes()
    data_0.write(noise_data)
    data_1.write(noise_data)

    # cs_twirl.run(gx, gy)
    cs_median.run(gx, gy)

    data_0 = np.frombuffer(data_0.read(), dtype=np.float32)
    data_0 = np.multiply(data_0, 255.0)
    data_0 = data_0.reshape((u_height, u_width, 4))
    data_0 = data_0[::-1]
    data_0 = data_0.astype(np.uint8)
    ii.imwrite("data_0.png", data_0)

    data_1 = np.frombuffer(data_1.read(), dtype=np.float32)
    data_1 = np.multiply(data_1, 255.0)
    data_1 = data_1.reshape((u_height, u_width, 4))
    data_1 = data_1[::-1]
    data_1 = data_1.astype(np.uint8)
    ii.imwrite("data_1.png", data_1)

    print("render finished!")


def try_render():
    print("trying to render..")
    try:
        render()
        print("rendering finished!")
    except Exception as e:
        print(e)


def main():
    render()

    # class Handler(FileSystemEventHandler):
    #     def __init__(self, callback):
    #         super(Handler, self).__init__()
    #         self.on_modified = callback

    # observer = Observer()
    # observer.schedule(Handler(lambda e: try_render()), "./gl")
    # observer.start()
    # observer.join()


if __name__ == "__main__":
    main()
