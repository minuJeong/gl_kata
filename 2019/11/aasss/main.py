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
    def __init__(self, window, width, height):
        super(Render, self).__init__()

        self.window = window
        self.width, self.height = width, height

        self.gl = mg.create_context()

        self.build_quad()
        self.compile()

        def onmod(e):
            self.need_compile = True

        h = FileSystemEventHandler()
        h.on_modified = onmod
        ob = Observer()
        ob.schedule(h, "./gl/", True)
        ob.start()

    def build_quad(self):
        vertices = [-1.0, -1.0, -1.0, +1.0, +1.0, -1.0, +1.0, +1.0]
        self.vbo = self.gl.buffer(np.array(vertices).astype(np.float32).tobytes())

        indices = [0, 1, 2, 2, 1, 3]
        self.ibo = self.gl.buffer(np.array(indices).astype(np.int32).tobytes())

    def compile(self):
        self.need_compile = False
        try:
            vs, fs = read_shader("./gl/vs_aaa.glsl"), read_shader("./gl/fs_aaa.glsl")
            self.program = self.gl.program(vertex_shader=vs, fragment_shader=fs)
            self.vao = self.gl.vertex_array(
                self.program, [(self.vbo, "2f", "in_pos")], self.ibo
            )
            print("compiled")

        except Exception as e:
            print(e)

    def uniform(self, n, v):
        if n in self.program:
            self.program[n].value = v

    def render(self):
        if self.need_compile:
            self.compile()

        self.uniform("u_time", glfw.get_time())

        self.vao.render()


def main():
    glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)

    width, height = 512, 512
    window = glfw.create_window(width, height, "", None, None)
    glfw.make_context_current(window)

    render = Render(window, width, height)

    # main loop
    while not glfw.window_should_close(window):
        render.render()
        glfw.poll_events()
        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
