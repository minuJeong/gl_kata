import struct

import moderngl as mg
import glfw

from glm import *

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Util(object):
    @staticmethod
    def bytes_float(value):
        assert isinstance(value, float)
        return struct.pack("f", value)


class Renderer(object):
    def __init__(self, gl_win, width, height):
        super(Renderer, self).__init__()

        self.window = gl_win
        self.width, self.height = width, height
        self.gl = mg.create_context()

        self.vbo = self.gl.buffer(reserve=4 * 4 * 4)
        self.ibo = self.gl.buffer(reserve=6 * 4)

        self.vbo.bind_to_storage_buffer(0)
        self.ibo.bind_to_storage_buffer(1)

        self.const = self.gl.buffer(reserve=1024)
        self.const.bind_to_storage_buffer(15)

        self.build_vao()

        def onmod(e):
            self.should_compile = True

        h = FileSystemEventHandler()
        h.on_modified = onmod
        o = Observer()
        o.schedule(h, "./gl/", True)
        o.start()

    def read_shader(self, path):
        with open(path, "r") as fp:
            return fp.read()

    def build_vao(self):
        self.should_compile = False
        try:
            self.mesh_builder = self.gl.compute_shader(
                self.read_shader("./gl/cs_build_screen.glsl")
            )

            screen_program = self.gl.program(
                vertex_shader=self.read_shader("./gl/vs_screen.glsl"),
                fragment_shader=self.read_shader("./gl/fs_screen.glsl"),
            )

            self.vao = self.gl.vertex_array(
                screen_program, [(self.vbo, "2f", "in_pos")], self.ibo, skip_errors=True
            )

            print("compiled vao")

        except Exception as e:
            print(e)

    def gpu_const(self, offset, value):
        self.const.write(value, offset=offset)

    def render(self):
        if self.should_compile:
            self.build_vao()
            self.mesh_builder.run(1)

        self.gpu_const(0, Util.bytes_float(glfw.get_time()))
        self.vao.render()


def main():
    glfw.init()

    width, height = 512, 512
    title = "안녕"

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    gl_win = glfw.create_window(width, height, title, None, None)
    glfw.make_context_current(gl_win)

    renderer = Renderer(gl_win, width, height)
    while not glfw.window_should_close(gl_win):

        renderer.render()

        glfw.poll_events()
        glfw.swap_buffers(gl_win)


if __name__ == "__main__":
    main()
