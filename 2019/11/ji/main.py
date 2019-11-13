import numpy as np
import moderngl as mg
import glfw
from glm import *

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def read_file(path):
    with open(path, "r") as fp:
        return fp.read()


class Renderer(object):
    def __init__(self, window):
        super(Renderer, self).__init__()
        self.window = window

    def init_gl(self):
        self.gl = mg.create_context()

        self.vbo = self.gl.buffer(
            np.array(
                [-1.0, -1.0, 0.0, -1.0, +1.0, 0.0, +1.0, -1.0, 0.0, +1.0, +1.0, 0.0]
            )
            .astype(np.float32)
            .tobytes()
        )
        self.ibo = self.gl.buffer(
            np.array([0, 1, 2, 2, 1, 3]).astype(np.int32).tobytes()
        )

        self.recompile()

        width, height = glfw.get_window_size(self.window)
        self.uniform("u_resolution", vec2(width, height))

        self.wire_events()

        def on_mod(e):
            self.should_recompile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_mod
        self.observer = Observer()
        self.observer.schedule(handler, "./gl/", True)
        self.observer.start()

    def recompile(self):
        self.should_recompile = False

        try:
            self.program = self.gl.program(
                vertex_shader=read_file("./gl/vs_screen.glsl"),
                fragment_shader=read_file("./gl/fs_screen.glsl"),
            )

            self.vao = self.gl.vertex_array(
                self.program, [(self.vbo, "3f", "in_pos")], self.ibo
            )

            print("--- shader recompiled ---")

        except Exception as e:
            print(e)

    def wire_events(self):
        glfw.set_window_size_callback(self.window, self.on_window_size)

    def uniform(self, n, v):
        print(self.program)
        BIN_TYPES = (vec2, vec3, vec4, mat4)
        if n in self.program:
            if isinstance(v, BIN_TYPES):
                self.program[n].write(bytes(v))
            else:
                self.program[n].value = v

    def paint_gl(self):
        if self.should_recompile:
            self.recompile()

        self.gl.clear()
        self.uniform("u_time", glfw.get_time())
        self.vao.render()

    def on_window_size(self, window, width, height):
        self.gl.viewport = (0, 0, width, height)
        self.uniform("u_resolution", vec2(width, height))


def main():
    glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(500, 500, "title", None, None)
    glfw.make_context_current(window)

    renderer = Renderer(window)
    renderer.init_gl()

    while not glfw.window_should_close(window):
        renderer.paint_gl()
        glfw.swap_buffers(window)
        glfw.poll_events()


if __name__ == "__main__":
    main()
