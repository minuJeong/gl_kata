
from threading import Thread
from threading import Event
from queue import Queue

import moderngl as mg
import numpy as np
import imageio as ii


class Recorder(Thread):

    data_flow = Queue()
    finish_event = Event()

    def __init__(self, u_width, u_height, u_channel):
        super(Recorder, self).__init__()
        self.finish_event.clear()
        self.u_width, self.u_height, self.u_channel = u_width, u_height, u_channel

    def push(self, data):
        self.data_flow.put(data)

    def serialize(self):
        data = self.data_flow.get()

        data = np.frombuffer(data, dtype="f4")
        data = np.multiply(data, 255.0)
        data = data.reshape((self.u_width, self.u_height, self.u_channel))
        data = data.astype(np.uint8)

        return data

    def run(self):
        ii_writer = ii.get_writer("recorded.mp4", fps=30)
        while True:
            if self.data_flow.empty():
                if self.finish_event.is_set():
                    break
                continue

            ii_writer.append_data(
                self.serialize()
            )

        ii_writer.close()


def read(path):
    with open(path, 'r') as fp:
        return fp.read()


def init(u_width, u_height, u_channel):
    gl = mg.create_standalone_context()
    cs = gl.compute_shader(read("./gl/compute.glsl"))

    gx, gy = int(u_width / 8), int(u_height / 8)

    if "u_width" in cs:
        cs["u_width"].value = u_width

    if "u_height" in cs:
        cs["u_height"].value = u_height

    output = gl.buffer(reserve=u_width * u_height * 4 * 4)
    output.bind_to_storage_buffer(0)

    return cs, gx, gy, output


def render(i, cs, gx, gy):
    if "u_time" in cs:
        cs["u_time"].value = i
    cs.run(gx, gy)


def main():
    u_width, u_height, u_channel = 512, 512, 4
    serializer = Recorder(u_width, u_height, u_channel)
    serializer.start()

    cs, gx, gy, output = init(u_width, u_height, u_channel)

    for i in range(120):
        render(i, cs, gx, gy)
        serializer.push(output.read())

    serializer.finish_event.set()

if __name__ == "__main__":
    main()
