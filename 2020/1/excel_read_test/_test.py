import moderngl as mg
import numpy as np
from PyQt5 import QtWidgets


class Render(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(Render, self).__init__()
        self.setMinimumSize(1024, 1024)

    def initializeGL(self):
        self.gl = mg.create_context()
        VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
        program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
        vb = self.gl.buffer(np.array([-1, -1, -1, 1, 1, -1, 1, 1], dtype=np.float32))
        ib = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))
        self.va = self.gl.vertex_array(program, [(vb, "2f", "in_pos")], ib, skip_errors=True)

    def paintGL(self):
        self.va.render()


def main():
    app = QtWidgets.QApplication([])
    render = Render()
    render.show()
    app.exec()


if __name__ == "__main__":
    main()
