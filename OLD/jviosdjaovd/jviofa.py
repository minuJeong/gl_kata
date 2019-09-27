"""
author: minu jeong
"""

import numpy as np
import moderngl as mg
import glfw

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Renderer(object):
    def __init__(self):
        super(Renderer, self).__init__()

    def start(self):
        glfw.init()

        glfw.window_hint(glfw.FLOATING, glfw.TRUE)
        window = glfw.create_window(400, 400, "GLFW Window", None, None)
        glfw.make_context_current(window)

        self.init()

        while not glfw.window_should_close(window):

            if self.should_recompile:
                self.recompile()
            self.render()

            glfw.swap_buffers(window)
            glfw.poll_events()

        print("Done!")

    def set_recompile_flag(self, should_recompile):
        self.should_recompile = should_recompile

    def read(self, path):
        with open(path, "r") as fp:
            return fp.read()

    def recompile(self):
        self.should_recompile = False

        self.program = self.gl.program(
            vertex_shader=self.read("./gl/verts.glsl"),
            fragment_shader=self.read("./gl/frags.glsl"),
        )

        self.vao = self.gl.vertex_array(self.program, self.vbo, self.ibo)

    def init(self):
        self.gl = mg.create_context()

        self.vbo = [
            (
                self.gl.buffer(
                    np.array([-1.0, -1.0, -1.0, +1.0, +1.0, -1.0, +1.0, +1.0])
                    .astype(np.float32)
                    .tobytes()
                ),
                "2f",
                "in_pos",
            )
        ]

        self.ibo = self.gl.buffer(
            np.array([0, 1, 2, 2, 1, 3]).astype(np.int32).tobytes()
        )

        self.recompile()

        handler = FileSystemEventHandler()
        handler.on_modified = lambda e: self.set_recompile_flag(True)
        observer = Observer()
        observer.schedule(handler, "./gl/")
        observer.start()

    def render(self):
        self.vao.render()


def main():
    renderer = Renderer()
    renderer.start()


if __name__ == "__main__":
    main()
