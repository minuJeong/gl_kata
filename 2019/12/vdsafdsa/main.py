import glfw
import moderngl as mg
import numpy as np
from glm import *

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


WIDTH, HEIGHT = 1920 // 2, 1080 // 2


def read(path):
    with open(path, "r") as fp:
        return fp.read()


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window

        self.gl = mg.create_context()

        self.volume_res = ivec3(128, 128, 128)
        self.compute_group_res = self.volume_res / 8

        self.compile()

        # start shader code observer
        h = FileSystemEventHandler()
        h.on_modified = self.on_modified
        o = Observer()
        o.schedule(h, "./gl/", True)
        o.start()

    def on_modified(self, e):
        self.shader_should_compile = True

    def compile(self):
        self.shader_should_compile = False

        gl = self.gl

        try:
            self.cs_truchet = gl.compute_shader(read("./gl/truchet.compute"))
            self.p_render = gl.program(
                vertex_shader=read("./gl/pass.vert"),
                fragment_shader=read("./gl/render.frag"),
            )

            vbdata = (
                np.array([-1.0, -1.0, +1.0, -1.0, -1.0, +1.0, +1.0, +1.0])
                .astype(np.float32)
                .tobytes()
            )
            ibdata = np.array([0, 1, 2, 2, 1, 3]).astype(np.int32).tobytes()
            vb, ib = gl.buffer(vbdata), gl.buffer(ibdata)
            self.vao = gl.vertex_array(self.p_render, [(vb, "2f", "in_pos")], ib, skip_errors=True)

            print("compiled")

        except Exception as e:
            print(e)

    def update(self):
        if self.shader_should_compile:
            self.compile()

        self.cs_truchet.run(*self.compute_group_res)
        self.vao.render()


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(512, 512, "hello", None, None)
    glfw.make_context_current(window)
    client = Client(window)
    while not glfw.window_should_close(window):
        client.update()
        glfw.poll_events()
        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
