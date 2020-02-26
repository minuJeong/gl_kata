import struct

import moderngl as mg
import glfw
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window
        self.gl = mg.create_context()

        self._compile_shader()

        def onmod(e):
            self._should_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = onmod
        observer = Observer()
        observer.schedule(handler, "./gl/", True)
        observer.start()

    def _compile_shader(self):
        self._should_compile = False
        try:
            VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            vertices_data = struct.pack(
                "16f",
                *vec4(-1.0, -1.0, 0.0, 1.0),
                *vec4(-1.0, +1.0, 0.0, 1.0),
                *vec4(+1.0, -1.0, 0.0, 1.0),
                *vec4(+1.0, +1.0, 0.0, 1.0)
            )
            vertices = self.gl.buffer(vertices_data)
            content = [(vertices, "4f", "in_pos")]
            indices_data = struct.pack("6i", 0, 1, 2, 2, 1, 3)
            indices = self.gl.buffer(indices_data)
            self.vao = self.gl.vertex_array(program, content, indices)
            print("compiled shader")

        except Exception as e:
            print(e)

    def _render(self):
        self.gl.clear()
        self.gl.enable(mg.BLEND)
        self.vao.render()

    def update(self):
        if self._should_compile:
            self._compile_shader()
            return

        self._render()


def main():
    width, height = 400, 400
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(width, height, "", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
