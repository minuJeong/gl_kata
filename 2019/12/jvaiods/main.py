from struct import pack

import numpy as np
import moderngl as mg
import imageio as ii
import glfw
from glm import *

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


WIDTH, HEIGHT = 512, 512


def read(path):
    with open(path, "r") as fp:
        return fp.read()


def load_texture_data(path):
    img = ii.imread(path)
    return img.tobytes()


class Client(object):
    gl = None

    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window

        Client.gl = Client.gl or mg.create_context()
        self.compile_shaders()

        glfw.set_key_callback(window, self.on_key)

        h = FileSystemEventHandler()
        h.on_modified = self.on_modified
        o = Observer()
        o.schedule(h, "./gl/", True)
        o.start()

    def on_modified(self, e):
        self.should_compile = True

    def on_key(self, window, scancode, keycode, action, mods):
        if action == glfw.RELEASE:
            if scancode == glfw.KEY_SPACE:
                self.take_screenshot()

    def uniform(self, p, n, v):
        if n not in p:
            return

        p[n].value = v

    def compile_shaders(self):
        self.should_compile = False

        gl = Client.gl

        try:
            VS, FS = "./gl/quad.vs", "./gl/quad.fs"
            self.program = gl.program(vertex_shader=read(VS), fragment_shader=read(FS))
            vb = gl.buffer(
                np.array(
                    [
                        (-1.0, -1.0, 0.0, 1.0),
                        (+1.0, -1.0, 0.0, 1.0),
                        (-1.0, +1.0, 0.0, 1.0),
                        (+1.0, +1.0, 0.0, 1.0),
                    ]
                )
                .astype(np.float32)
                .tobytes()
            )
            ib = gl.buffer(pack("6i", 0, 1, 2, 2, 1, 3))
            self.vao = gl.vertex_array(self.program, [(vb, "4f", "in_pos")], ib, skip_errors=True)

            self.uniform(self.program, "u_aspect", WIDTH / HEIGHT)

            self.tex = gl.texture((512, 512), 3, load_texture_data("./res/scratch_1.png"))
            self.tex.use(0)

            print("shaders compiled")

        except Exception as e:
            print(e)

    def update(self):
        if self.should_compile:
            self.compile_shaders()

        self.uniform(self.program, "u_heightmap", 0)
        self.vao.render()

    def take_screenshot(self):
        fb = Client.gl.screen
        data = fb.read()

        img = np.frombuffer(data, dtype=np.ubyte)
        img = img.reshape((HEIGHT, WIDTH, 3))
        img = img[::-1]
        ii.imwrite("luminosity.png", img)

        print("screenshot saved!")


def main():
    glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, "tex comb", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        client.update()
        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
