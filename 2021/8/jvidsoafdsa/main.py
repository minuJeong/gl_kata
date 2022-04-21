import glfw
import moderngl as mg
import numpy as np


class Client:
    def __init__(self, window):
        super().__init__()

        self.window = window
        self.gl = mg.create_context()
        self.init()

    def init(self):
        try:
            VS, FS = open("./gl/quad_vs.glsl").read(), open("./gl/quad_fs.glsl").read()
            vertex_buffer = self.gl.buffer(
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
            index_buffer = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.uint32))

            self.quad = self.gl.vertex_array(
                self.gl.program(vertex_shader=VS, fragment_shader=FS),
                [(vertex_buffer, "4f", "in_pos")],
                index_buffer,
            )

        except Exception as e:
            print(e)

    def uniform(self, program, uname, uvalue):
        if uname not in program:
            return

        program[uname].value = uvalue

    def update(self):
        self.uniform(self.quad.program, "u_time", glfw.get_time())
        self.quad.render()


def main():
    assert glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(512, 512, "", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.swap_buffers(window)
        glfw.poll_events()

        client.update()


if __name__ == "__main__":
    main()
