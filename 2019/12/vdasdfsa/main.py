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
        o.schedule(h, "./gl/", True)
        o.start()

    def compile(self):
        self.should_compile = False

        try:
            NUM_QUAD = 10

            VS, FS = read("./gl/quad.vs"), read("./gl/quad.fs")
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            vb = self.gl.buffer(reserve=(4 + 4 + 4) * 4 * NUM_QUAD * 4)
            vb.bind_to_storage_buffer(0)

            indices = []
            for i in range(NUM_QUAD):
                ofs = i * 4
                indices.extend([0 + ofs, 1 + ofs, 2 + ofs, 2 + ofs, 1 + ofs, 3 + ofs])

            ib = self.gl.buffer(np.array(indices, dtype=np.int32))
            self.vao = self.gl.vertex_array(
                program,
                [(vb, "4f 4f 4f", "in_pos", "in_uv", "in_color")],
                ib,
                skip_errors=True,
            )

            CS = read("./gl/mesh.cs")
            self.cs = self.gl.compute_shader(CS)
            self.group = NUM_QUAD, 1

            u_aspect = self.width / self.height
            self.uniform(program, "u_aspect", u_aspect)
            self.uniform(self.cs, "u_aspect", u_aspect)

            print("done")

        except Exception as e:
            print(e)

    def uniform(self, p, n, v):
        if n not in p:
            return

        if isinstance(v, (float, int)):
            p[n].value = v

        else:
            p[n].write(bytes(v))

    def update(self):
        if self.should_compile:
            self.compile()
            return

        self.gl.clear()

        u_time = glfw.get_time()
        self.uniform(self.vao.program, "u_time", u_time)
        self.uniform(self.cs, "u_time", u_time)

        self.cs.run(*self.group)
        self.vao.render()


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(1920, 1080, "", None, None)
    glfw.make_context_current(window)
    client = Client(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
