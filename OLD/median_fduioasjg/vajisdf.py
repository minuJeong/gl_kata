
import numpy as np
import moderngl as mg

from PyQt5 import QtWidgets
from PyQt5.QtGui import QCursor
from PyQt5.QtGui import QScreen
from PyQt5.QtCore import Qt


u_width, u_height = 512, 512


class Render(QtWidgets.QOpenGLWidget):

    def __init__(self):
        super(Render, self).__init__()
        self.setMinimumSize(u_width, u_height)
        self.setMaximumSize(u_width, u_height)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

    def read(self, path):
        with open(path, 'r') as fp:
            return fp.read()

    def initializeGL(self):
        self.gl = mg.create_context()
        p = self.gl.program(
            vertex_shader=self.read("./gl/vtx.glsl"),
            fragment_shader=self.read("./gl/frag.glsl")
        )
        vbo = [
            -1.0, -1.0,
            +1.0, -1.0,
            -1.0, +1.0,
            +1.0, +1.0,
        ]
        vbo = np.array(vbo).astype(np.float32).tobytes()
        content = [(
            self.gl.buffer(vbo), "2f", "in_pos"
        )]

        ibo = [0, 1, 2, 2, 1, 3]
        ibo = np.array(ibo).astype(np.int32).tobytes()
        ibo = self.gl.buffer(ibo)

        random_data = np.random.uniform(0.0, 1.0, (u_width, u_height, 4))
        random_data = random_data.astype(np.float32)
        random_data[:, :, -1] = 1.0

        self.texture = self.gl.texture((u_width, u_height), 4, dtype="f4")
        self.texture.write(random_data)

        self.vao = self.gl.vertex_array(p, content, ibo)

    def paintGL(self):
        self.texture.use(0)
        self.vao.render()
        self.update()

        p = self.mapFromGlobal(QCursor.pos())
        print(p.x(), p.y())


def main():
    app = QtWidgets.QApplication([])
    render = Render()
    render.show()
    app.exec()


if __name__ == "__main__":
    main()
