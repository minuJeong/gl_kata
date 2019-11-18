import moderngl as mg
import numpy as np
import glfw
from glm import *

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def read_shader(path):
    with open(path, "r") as fp:
        return fp.read()


class RenderContext(object):
    def __init__(self, window, width, height):
        super(RenderContext, self).__init__()

        self.window = window
        self.width, self.height = width, height

        self.gl = mg.create_context()

        self.build_vao()

        def onmod(e):
            self.need_compile = True

        h = FileSystemEventHandler()
        h.on_modified = onmod
        o = Observer()
        o.schedule(h, "./gl/", True)
        o.start()

        self.on_win_size(self.window, self.width, self.height)
        glfw.set_window_size_callback(self.window, self.on_win_size)

    def build_vao(self):
        self.need_compile = False
        try:
            vs, fs = read_shader("./gl/vs_aaa.glsl"), read_shader("./gl/fs_aaa.glsl")
            self.program = self.gl.program(vertex_shader=vs, fragment_shader=fs)

            vertices = np.array([-1.0, -1.0, -1.0, +1.0, +1.0, -1.0, +1.0, +1.0])
            self.vbo = self.gl.buffer(vertices.astype(np.float32).tobytes())
            content = [(self.vbo, "2f", "in_pos")]

            indices = [0, 1, 2, 2, 1, 3]
            self.ibo = self.gl.buffer(np.array(indices).astype(np.int32).tobytes())
            self.vao = self.gl.vertex_array(
                self.program, content, self.ibo, skip_errors=True
            )

            self.uniform("u_aspect", self.width / self.height)
            print("compiled!")

        except Exception as e:
            print(e)

    def uniform(self, n, v):
        if n in self.program:
            self.program[n].value = v

    def render(self):
        if self.need_compile:
            self.build_vao()

        self.uniform("u_time", glfw.get_time())

        self.gl.clear()
        self.vao.render()

    def on_win_size(self, win, wid, hei):
        self.gl.viewport = (0, 0, wid, hei)
        self.width, self.height = wid, hei
        self.uniform("u_aspect", self.width / self.height)


def main():
    glfw.init()

    width, height = 1024, 1024

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    w = glfw.create_window(width, height, "", None, None)
    glfw.make_context_current(w)

    render = RenderContext(w, width, height)

    while not glfw.window_should_close(w):
        render.render()

        glfw.poll_events()
        glfw.swap_buffers(w)


if __name__ == "__main__":
    main()
