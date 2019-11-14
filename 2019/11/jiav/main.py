import moderngl as mg
import numpy as np
import glfw
from glm import *

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def read_shader(path):
    with open(path, "r") as fp:
        return fp.read()


class Render(object):
    def __init__(self, window):
        super(Render, self).__init__()

    def init(self):
        self.gl = mg.create_context()

        self.build_vao()

        def on_mod(e):
            self.should_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_mod
        ob = Observer()
        ob.schedule(handler, "./gl/", True)
        ob.start()

    def build_vao(self):
        self.should_compile = False

        try:
            self.program = self.gl.program(
                vertex_shader=read_shader("./gl/vs_aaa.glsl"),
                fragment_shader=read_shader("./gl/fs_aaa.glsl"),
            )

            vertices = [-1.0, -1.0, -1.0, +1.0, +1.0, -1.0, +1.0, +1.0]
            indices = [0, 1, 2, 2, 1, 3]

            vertices = np.array(vertices).astype(np.float32).tobytes()
            indices = np.array(indices).astype(np.int32).tobytes()
            self.vao = self.gl.vertex_array(
                self.program,
                [(self.gl.buffer(vertices), "2f", "in_pos")],
                self.gl.buffer(indices),
                skip_errors=True,
            )
            print("compiled")

        except Exception as e:
            print(e)

    def uniform(self, n, v):
        if n in self.program:
            self.program[n].value = v

    def render(self):
        if self.should_compile:
            self.build_vao()

        self.uniform("u_time", glfw.get_time())

        self.vao.render()


def main():
    glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)

    width, height = 512, 512
    title = "hello"
    window = glfw.create_window(width, height, title, None, None)
    glfw.make_context_current(window)
    render = Render(window)
    render.init()

    while not glfw.window_should_close(window):
        render.render()

        glfw.poll_events()
        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
