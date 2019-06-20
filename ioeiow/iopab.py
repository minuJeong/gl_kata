
from threading import Thread
from threading import Event
from queue import Queue

import moderngl as mg
import numpy as np
import imageio as ii


u_width, u_height = 1024, 1024


def read(path):
    with open(path, 'r') as fp:
        return fp.read()


def set_uniform(prog, key, value):
    if prog and key in prog:
        prog[key].value = value


def serialize(data):
    data = np.frombuffer(data, dtype=np.float32)
    data = data.reshape((u_height, u_width, 4))
    data = np.multiply(data, 255.0)
    data = data.astype(np.uint8)
    return data


class Recorder(Thread):

    queue = Queue()
    done_event = Event()

    def __init__(self):
        super(Recorder, self).__init__()

    def put(self, data):
        self.queue.put(data)

    def run(self):
        self.done_event.clear()

        recorder = ii.get_writer("output.mp4", fps=30)

        while True:
            if self.queue.empty():
                if self.done_event.is_set():
                    break
                continue

            data = serialize(self.queue.get())
            recorder.append_data(data)

        recorder.close()


def main():
    gl = mg.create_standalone_context()
    compute = gl.compute_shader(read("./gl/compute.glsl"))

    set_uniform(compute, "u_width", u_width)
    set_uniform(compute, "u_height", u_height)

    buffer_0 = gl.buffer(reserve=u_width * u_height * 4 * 4)
    buffer_0.bind_to_storage_buffer(0)

    gx, gy = int(u_width / 8), int(u_height / 8)

    recorder = Recorder()
    recorder.start()
    for i in range(20):
        set_uniform(compute, "u_time", i)
        compute.run(gx, gy)
        recorder.put(buffer_0.read())

    ii.imwrite("output_2.png", serialize(buffer_0.read()))

    recorder.done_event.set()


if __name__ == "__main__":
    main()
