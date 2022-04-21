import glfw
import numpy as np
import moderngl as mg
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from const import WIDTH, HEIGHT


class Client:
    def __init__(self, window):
        super().__init__()

        self.window = window

        self.gl = mg.create_context()
        self.init_gl()

        def on_mod(e):
            self.should_compile = True

        h = FileSystemEventHandler()
        h.on_modified = on_mod
        o = Observer()
        o.schedule(h, "./gl/", True)
        o.start()

    def init_gl(self):
        self.should_compile = False

        try:
            VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            vertices = self.gl.buffer(
                np.array(
                    [
                        [-1.0, -1.0, 0.0, 1.0],
                        [+1.0, -1.0, 0.0, 1.0],
                        [-1.0, +1.0, 0.0, 1.0],
                        [+1.0, +1.0, 0.0, 1.0],
                    ],
                    dtype=np.float32,
                )
            )
            indices = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))
            self.quad = self.gl.vertex_array(program, [(vertices, "4f", "in_pos")], indices)
            self.uniform("u_resolution", (WIDTH, HEIGHT))

        except Exception as e:
            print(e)

        print("init_gl")

    def uniform(self, uname, uvalue):
        p = self.quad.program
        if uname not in p:
            return

        p[uname].value = uvalue

    def update(self):
        if self.should_compile:
            self.init_gl()
            return

        self.uniform("u_time", glfw.get_time())
        self.quad.render()


def main():
    assert glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, "Render Demo", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
