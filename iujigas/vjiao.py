import moderngl as mg
import numpy as np

from PyQt5 import QtWidgets


class Renderer(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(Renderer, self).__init__()
        self.u_width, self.u_height = 512, 512
        self.gx, self.gy = int(self.u_width / 8), int(self.u_height / 8)
        self.setMinimumSize(self.u_width, self.u_height)

    def read(self, path):
        with open(path, "r") as fp:
            return fp.read()

    def initializeGL(self):
        self.gl = mg.create_context()

        program = self.gl.program(
            vertex_shader=self.read("./gl/debug_vert.glsl"),
            fragment_shader=self.read("./gl/debug_frag.glsl"),
        )

        vbo = [-1.0, -1.0, -1.0, +1.0]
        vbo = np.array(vbo).astype(np.float32).tobytes()
        vbo = self.gl.buffer(vbo)

        contents = [(vbo, "2f", "in_pos")]

        ibo = [0, 1, 2, 2, 1, 3]
        ibo = np.array(ibo).astype(np.int32)
        ibo = self.gl.buffer(ibo)

        self.vao = self.gl.vertex_array(program, contents, ibo)

    def paintGL(self):
        self.vao.render()
        self.update()


def main():

    app = QtWidgets.QApplication([])
    renderer = Renderer()
    renderer.show()
    app.exec()


if __name__ == "__main__":
    main()
