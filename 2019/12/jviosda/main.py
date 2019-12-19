import numpy as np
import moderngl as mg
import glfw


def read(path):
    with open(path, "r") as fp:
        return fp.read(0)


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()

        self.window = window
        self.compile()

    def compile(self):
        self.gl = mg.create_context()
        vb = self.gl.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype=np.float32))
        ib = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))

        VS, FS = read("./gl/quad.vs"), read("./gl/quad.fs")
        program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
        self.vao = self.vertex_array(
            program, [(vb, "2f", "in_pos")], ib, skip_errors=True
        )

    def update(self):
        self.vao.render()


def main():
    width, height = 800, 600
    glfw.init()
    window = glfw.create_window(width, height, "title", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__name__":
    main()
