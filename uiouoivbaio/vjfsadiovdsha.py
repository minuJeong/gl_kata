
from itertools import product
from random import random
from threading import Thread
from threading import Event
from queue import Queue

import moderngl as mg
import numpy as np
import imageio as ii


u_width, u_height = 512, 512


def read_file(path):
    with open(path, 'r') as fp:
        return fp.read()


def set_uniform(shader, u_name, u_value):
    if shader is None:
        return

    if u_name in shader:
        shader[u_name].value = u_value


def serialize_buffer(data, shape):
    data_read = np.frombuffer(data, dtype=np.float32)
    data_read = np.multiply(data_read, 255.0)
    data_read = data_read.reshape(shape)
    data_read = data_read.astype(np.uint8)
    return data_read


def serialize_array(array, mul_255=True):
    if mul_255:
        array = np.multiply(array, 255.0)
    array = array.astype(np.uint8)
    return array


def visualize_voronoi_dots(array):
    img_array = np.zeros(shape=(u_height, u_width, 4))
    img_array[:, :, -1] = 1.0

    for dot in array:
        x, y = dot[0] * u_width, dot[1] * u_height

        SPREAD = 7
        pix_range = range(-SPREAD, SPREAD + 1)
        for ox, oy in product(pix_range, pix_range):
            dist = (ox * ox + oy * oy) / (SPREAD * SPREAD)
            dist = 1.0 - min(max(dist, 0.0), 1.0)

            px, py = x + ox, y + oy
            px, py = int(round(px)), int(round(py))
            px, py = min(max(px, 0), u_width - 1), min(max(py, 0), u_height - 1)

            old = img_array[py, px]
            img_array[py, px] = np.fmax(old, [dist, dist, dist, 1.0])

    img_array = np.multiply(img_array, 255.0)
    img_array = img_array.astype(np.uint8)
    ii.imwrite("voronoi_dots.png", img_array)


class Recorder(Thread):

    finish_event = Event()
    data_queue = Queue()

    def __init__(self, shape, fps=30):
        super(Recorder, self).__init__()

        self.shape = shape
        self.fps = fps

    def push(self, data):
        self.data_queue.put(data)

    def run(self):
        self.finish_event.clear()
        self.data_queue = Queue()

        mp4_writer = ii.get_writer("data_0.mp4", fps=self.fps)

        while True:
            if self.data_queue.empty():
                if self.finish_event.is_set():
                    break
                continue

            data = self.data_queue.get()
            if not data:
                continue

            data_read = serialize_buffer(data, self.shape)
            mp4_writer.append_data(data_read)

        mp4_writer.close()


def main():
    """
    issues 2 threads:
        - main thread is rendering thread holding compute shader
        - second thread put bytes array into mp4 format and save
        - communicate through Queue
    """

    gl = mg.create_standalone_context()

    data_shape = (u_height, u_width, 4)
    gx, gy = int(u_width / 8), int(u_height / 8)

    # setup data_0: output receiver buffer
    data_0 = gl.buffer(reserve=u_width * u_height * 4 * 4)
    data_0.bind_to_storage_buffer(0)

    # setup data_1: voronoi dot positions
    u_numdots = 200
    voronoi_random_dots = []
    for i in range(u_numdots):
        x, y, z = random(), random(), 0
        col = random()
        voronoi_random_dots.append((x, y, z, col))
    data_1_array = np.array(voronoi_random_dots).astype(np.float32)
    data_1 = gl.buffer(data_1_array)
    data_1.bind_to_storage_buffer(1)

    visualize_voronoi_dots(data_1_array)

    # compile compute shader
    cs = gl.compute_shader(read_file("./gl/compute.glsl"))

    # update uniform constants
    set_uniform(cs, "u_width", u_width)
    set_uniform(cs, "u_height", u_height)
    set_uniform(cs, "u_numdots", u_numdots)

    # init/start recorder: runs in separated thread, watching queue,
    # serialize buffer_0 into video
    FPS = 1
    recorder = Recorder(data_shape, fps=FPS)
    recorder.start()

    # run compute shader for gx * gy count
    FRAMES = 2
    for i in range(FRAMES):
        set_uniform(cs, "u_time", i % 1000)
        cs.run(gx, gy)

        # push buffer to recorder thread
        recorder.push(data_0.read())

    # wait for video encoding
    recorder.finish_event.set()
    recorder.join()

    # serialize last frame as debug image
    ii.imwrite("data_0.png", serialize_buffer(data_0.read(), data_shape))


if __name__ == "__main__":
    main()
