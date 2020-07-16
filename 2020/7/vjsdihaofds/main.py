import moderngl as mg
import numpy as np
import glfw


class Client(object):
    def __init__(self, window):
        super().__init__()

        self.gl = mg.create_context()

        VS, FS = open("./gl/quad.vs").read(), open("./gl/quad.fs").read()
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
        indices = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.uint))
        self.quad = self.gl.vertex_array(
            program, [(vertices, "4f", "in_pos")], indices, skip_errors=True
        )

    def update(self):
        self.quad.render()


def main():
    assert glfw.init()
    window = glfw.create_window(800, 800, "", None, None)
    glfw.make_context_current(window)
    client = Client(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
