from functools import reduce
from operator import add

import glfw
from glm import *
import numpy as np
import moderngl as mg
import imageio as ii
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window
        self.width, self.height = glfw.get_window_size(window)
        self.init()

    def init(self):
        self.gl = mg.create_context()

        self.compile()

        def on_mod(e):
            self.needcompile = True

        h = FileSystemEventHandler()
        h.on_modified = on_mod
        o = Observer()
        o.schedule(h, "./gl/", True)
        o.start()

    def compile(self):
        self.needcompile = False

        try:
            VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            vertices = (
                vec4(-1.0, -1.0, 0.0, 1.0),
                vec4(-1.0, +1.0, 0.0, 1.0),
                vec4(1.0, -1.0, 0.0, 1.0),
                vec4(1.0, 1.0, 0.0, 1.0),
            )
            indices = (
                ivec3(0, 1, 2),
                ivec3(2, 1, 3),
            )
            vertices = self.gl.buffer(reduce(add, map(bytes, vertices)))
            indices = self.gl.buffer(reduce(add, map(bytes, indices)))
            self.va = self.gl.vertex_array(program, [(vertices, "4f", "in_pos")], indices)
            self.uniform(program, "u_aspect", self.width / self.height)

            W, H = 32, 32
            tex_data = np.zeros((W, H, 4), dtype=np.ubyte)
            tex_data[:, :, 3] = 255
            for x in range(W):
                for y in range(H):
                    r = int(clamp(x / W, 0.0, 1.0) * 255.0)
                    g = int(clamp(y / H, 0.0, 1.0) * 255.0)
                    tex_data[x, y] = (r, g, 128, 255)

            tex = self.gl.texture((W, H), 4, tex_data.tobytes())
            tex.use(0)
            self.uniform(program, "u_texture", 0)

            print("compiled")

        except Exception as e:
            print(f"shader compile error: {e}")

    def uniform(self, program, uname, uvalue):
        if uname not in program:
            return

        program[uname] = uvalue

    def update(self):
        if self.needcompile:
            self.compile()
            return

        self.uniform(self.va.program, "u_time", glfw.get_time())
        self.va.render()


def main():
    WIDTH, HEIGHT = 800, 600

    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, "", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
