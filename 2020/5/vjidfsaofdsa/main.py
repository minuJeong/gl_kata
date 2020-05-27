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

        self.init()

    def init(self):
        self.gl = mg.create_context()

        self.compile_shaders()

        def on_mod(e):
            self.need_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_mod
        o = Observer()
        o.schedule(handler, "./gl/", True)
        o.start()

    def compile_shaders(self):
        self.need_compile = False

        try:
            VS, FS = open("./gl/quad.vs").read(), open("./gl/quad.fs").read()
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            v = struct.pack(
                "16f",
                *(
                    *vec4(-1.0, -1.0, 0.0, 1.0),
                    *vec4(-1.0, +1.0, 0.0, 1.0),
                    *vec4(+1.0, -1.0, 0.0, 1.0),
                    *vec4(+1.0, +1.0, 0.0, 1.0),
                ),
            )
            i = struct.pack("6i", 0, 1, 2, 2, 1, 3)
            self.quad = self.gl.vertex_array(program, [(self.gl.buffer(v), "4f", "in_pos")], self.gl.buffer(i))

            print("compiled")

        except Exception as e:
            print(e)

    def uniform(self, uname, uvalue):
        p = self.quad.program
        if uname not in p:
            return

        p[uname] = uvalue

    def update(self):
        if self.need_compile:
            self.compile_shaders()

        self.uniform("u_time", glfw.get_time())
        self.quad.render()


def main():
    assert glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(512, 512, "", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
