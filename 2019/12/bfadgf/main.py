import struct
import time

import numpy as np
import moderngl as mg
from glm import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5 import QtGui


def read_shader(path):
    with open(path, "r") as fp:
        return fp.read()


class Client(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(Client, self).__init__()

        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setMinimumSize(1024, 1024)
        self.setMaximumSize(1024, 1024)

        self.gl = None

    def initializeGL(self):
        self.gl = mg.create_context()

        vs, fs = read_shader("./gl/quad.vs"), read_shader("./gl/quad.fs")
        self.program = self.gl.program(vertex_shader=vs, fragment_shader=fs)
        self.vertices = self.gl.buffer(
            np.array(
                [
                    [-1.0, -1.0, 0.0, 1.0],
                    [-1.0, +1.0, 0.0, 1.0],
                    [+1.0, -1.0, 0.0, 1.0],
                    [+1.0, +1.0, 0.0, 1.0],
                ],
                dtype=np.float32,
            ).tobytes()
        )
        self.indices = self.gl.buffer(
            np.array([0, 1, 2, 2, 1, 3], dtype=np.int32).tobytes()
        )
        content = [(self.vertices, "4f", "in_pos")]
        self.vao = self.gl.vertex_array(self.program, content, self.indices)

        self.constbuffer = self.gl.buffer(reserve=8)
        self.constbuffer.bind_to_storage_buffer(14)

        w, h = self.width(), self.height()
        self.gl.viewport = (0, 0, w, h)
        self.constbuffer.write(struct.pack("f", w / h), offset=0)

    def render(self):
        self.vao.render()

    def paintGL(self):
        t = time.time() % 10000.0
        self.constbuffer.write(struct.pack("f", t), offset=4)

        self.update()
        self.render()

    def resizeEvent(self, e):
        if not self.gl:
            return

        w, h = self.width(), self.height()
        self.gl.viewport = (0, 0, w, h)
        self.const("u_aspect", w / h)

    def mousePressEvent(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.MiddleButton:
            self.isdrag = True
            self.prepos = ivec2(e.x(), e.y())

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.MiddleButton:
            self.isdrag = False

    def mouseMoveEvent(self, e: QtGui.QMouseEvent):
        if self.isdrag:
            pos = ivec2(e.globalX(), e.globalY())
            self.window().move(*(pos - self.prepos))


def main():
    app = QtWidgets.QApplication([])
    client = Client()
    client.show()
    app.exec()


if __name__ == "__main__":
    main()
