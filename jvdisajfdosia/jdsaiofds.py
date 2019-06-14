
from threading import Thread
from threading import Event
from queue import Queue

import moderngl as mg
import numpy as np
import imageio as ii


u_width, u_height, u_channel = 512, 512, 4


def _read_shader(path, **kargs):
    with open(path, 'r') as fp:
        context = fp.read()

    for a, b in kargs.items():
        context = context.replace(a, b)

    return context


def init():
    gl = mg.create_standalone_context()

    program = gl.program(
        vertex_shader=_read_shader("./gl/vert.glsl"),
        fragment_shader=_read_shader("./gl/frag.glsl")
    )

    vbo = [
        -1.0, -1.0, 0.0,
        -1.0, +1.0, 0.0,
        +1.0, -1.0, 0.0,
        +1.0, +1.0, 0.0,
    ]
    vbo = gl.buffer(np.array(vbo).astype(np.float32).tobytes())

    ibo = [0, 1, 2, 2, 1, 3]
    ibo = gl.buffer(np.array(ibo).astype(np.int32).tobytes())

    vao = gl.vertex_array(program, [(vbo, "3f", "in_pos")], ibo)

    frametex = gl.texture((u_width, u_height), u_channel, dtype="f4")
    frame = gl.framebuffer([frametex])
    scope = gl.scope(frame)

    return frame, scope, [vao]


def render(i, frame, scope, vaos):
    with scope:
        for vao in vaos:
            p = vao.program
            if "u_time" in p:
                p["u_time"].value = float(i)

            vao.render()

    data = bytearray(u_width * u_height * u_channel * 4)
    frame.read_into(data, None, 4, dtype="f4")
    return data


class Serializer(Thread):

    data_flow = Queue()
    _close_flag = Event()

    def __init__(self):
        super(Serializer, self).__init__()
        self._close_flag.clear()

    def push(self, data):
        self.data_flow.put(data)

    def run(self):
        recorder = ii.get_writer("record.mp4", fps=30)

        while True:
            if self.data_flow.empty():
                if self._close_flag.is_set():
                    break
                continue

            data = self.data_flow.get()
            if not data:
                continue

            data = np.frombuffer(data, dtype=np.float32)
            data = np.multiply(data, 255.0)
            data = data.reshape((u_width, u_height, u_channel))
            data = data.astype(np.uint8)
            recorder.append_data(data)

        recorder.close()


def main():
    frame, scope, vaos = init()

    serializer = Serializer()
    serializer.start()

    for i in range(100):
        data = render(i, frame, scope, vaos)
        serializer.push(data)

    serializer._close_flag.set()
    serializer.join()

if __name__ == "__main__":
    main()
