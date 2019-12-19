import glfw
import numpy as np
import moderngl as mg
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def read(path):
    with open(path, "r") as fp:
        return fp.read()


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()

        self.window = window
        self.width, self.height = glfw.get_window_size(window)

        self.gl = mg.create_context()
        self.compile()

        def on_modified(e):
            self.should_compile = True

        h = FileSystemEventHandler()
        h.on_modified = on_modified
        o = Observer()
        o.schedule(h, "./gl", True)
        o.start()

    def compile(self):
        self.should_compile = False
        try:
            VS, FS = read("./gl/quad.vs"), read("./gl/quad.fs")
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            vb = self.gl.buffer(
                np.array(
                    [-1.0, -1.0, -1.0, +1.0, +1.0, -1.0, +1.0, +1.0], dtype=np.float32
                ).tobytes()
            )
            ib = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32).tobytes())
            self.vao = self.gl.vertex_array(program, [(vb, "2f", "in_pos")], ib)

            self.uniform(program, "u_aspect", self.width / self.height)
            print("compiled")

        except Exception as e:
            print(e)

    def uniform(self, p, n, v):
        if n not in p:
            return

        if isinstance(v, (float, int)):
            p[n].value = v
        else:
            p[n].write(bytes(v))

    def render(self):
        if self.should_compile:
            self.compile()
            return

        self.uniform(self.vao.program, "u_time", glfw.get_time())
        self.vao.render()


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)

    window = glfw.create_window(1920, 1280, "", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        client.render()
        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
