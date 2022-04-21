import struct
import time
from threading import Thread
from queue import Queue

import cv2
import numpy as np
import moderngl as mg
import glfw
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import sounddevice as sd


WIDTH, HEIGHT = 800, 600
SAMPLERATE = 44100
DEVICE = 6


class AudioThread(Thread):
    def __init__(self):
        super().__init__()
        self.data = Queue()
        self.should_close = False

    def put(self, data):
        self.data.put(data)

    def callback(self, output, frames, time, status):
        data = self.data.get().reshape((-1, 1))
        output[:] = data

    def run(self):
        super().__init__()

        self.idx = 0
        self.output = sd.OutputStream(device=DEVICE, channels=1, callback=self.callback, samplerate=SAMPLERATE)
        self.output.start()

        while not self.should_close:
            pass

        self.output.stop()

    def dispose(self):
        self.should_close = True


class ComputeAudioGen:
    def __init__(self, gl):
        super().__init__()
        self.gl = gl

        self.program = gl.compute_shader(open("./gl/compute.glsl").read())
        self.audio_buffer = gl.buffer(reserve=1136 * 4)
        self.audio_buffer.bind_to_storage_buffer(0)

        self.u_count = 0

    def uniform(self, uname, uvalue):
        p = self.program
        if uname not in p:
            return

        p[uname].value = uvalue

    def render(self):
        self.uniform("u_count", self.u_count)
        self.program.run(156)

    def get_data(self):
        return np.frombuffer(self.audio_buffer.read(), dtype=np.float32)


class Client:
    def __init__(self, window):
        super().__init__()

        self.window = window
        self.video_capture = cv2.VideoCapture(0)
        self.gl = mg.create_context(require=460)

        self.init()

        self.need_init = False

        def invalidate_init():
            self.need_init = True

        h = FileSystemEventHandler()
        h.on_modified = lambda e: invalidate_init()
        o = Observer()
        o.schedule(h, "./gl/", True)
        o.start()

        self.audio = AudioThread()
        self.audio.start()

    def init(self):
        self.need_init = False

        self.vaos = []
        try:
            VS, FS = open("./gl/vert.glsl").read(), open("./gl/frag.glsl").read()
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            vb = self.gl.buffer(
                struct.pack("16f", -1, -1, 0, 1, -1, 1, 0, 1, 1, -1, 0, 1, 1, 1, 0, 1)
            )
            ib = self.gl.buffer(struct.pack("6i", 0, 1, 2, 2, 1, 3))
            self.vaos.append(self.gl.vertex_array(program, [(vb, "4f", "in_pos")], ib))

            self.audio_gen = ComputeAudioGen(self.gl)
            self.vaos.append(self.audio_gen)

            self.uniform("u_resolution", glfw.get_window_size(self.window))

            print("init")

        except Exception as e:
            print(e)

    def uniform(self, uname, uvalue):
        for quad in self.vaos:
            p = quad.program
            if uname in p:
                p[uname].value = uvalue

    def render(self):
        for quad in self.vaos:
            quad.render()

    def update(self):
        if self.need_init:
            return self.init()

        t = glfw.get_time()

        self.uniform("u_time", t)
        self.handle_cv()
        self.handle_audio()
        self.render()

    def handle_cv(self):
        is_success, self.img = self.video_capture.read()
        if is_success:
            size = self.img.shape[1], self.img.shape[0]
            self.tex = self.gl.texture(size, self.img.shape[2], self.img)
            self.uniform("u_tex_0_resolution", size)
            self.uniform("u_tex_0", 0)
            self.tex.use(0)

    def handle_audio(self):
        self.audio.put(self.audio_gen.get_data())

    def dispose(self):
        self.audio.dispose()


def main():
    assert glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, "", None, None)
    glfw.make_context_current(window)
    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()
    client.dispose()


if __name__ == "__main__":
    main()
