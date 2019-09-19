import numpy as np
import moderngl as mg
import glfw


class Render(object):
    def read(self, path):
        with open(path, 'r') as fp:
            return fp.read()

    def __init__(self, width, height):
        super(Render, self).__init__()

        self.GL = mg.create_context()

        # vertex buffer object
        vbo = np.array([-1.0, -1.0, +1.0, -1.0, -1.0, +1.0, +1.0, +1.0])\
                .astype(np.float32)\
                .tobytes()

        # index buffer object
        ibo = np.array([0, 1, 2, 2, 1, 3]).astype(np.int32).tobytes()

        program = self.GL.program(
            # geometry_shader, tessellation_shader..
            vertex_shader=self.read("./gl/vertex.glsl"),
            fragment_shader=self.read("./gl/frags.glsl")
        )

        if "u_resolution" in program:
            program["u_resolution"].value = (width, height)

        self.mesh = self.GL.vertex_array(
            program,
            [(self.GL.buffer(vbo), "2f", "in_position")],
            self.GL.buffer(ibo))

    def render(self):
        self.mesh.render()


def main():
    glfw.init()
    width, height = 608, 400
    title = "hello glfw"
    window = glfw.create_window(width, height, title, None, None)
    glfw.make_context_current(window)

    render = Render(608, 400)

    while not glfw.window_should_close(window):

        render.render()

        glfw.swap_buffers(window)
        glfw.poll_events()


if __name__ == "__main__":
    main()
