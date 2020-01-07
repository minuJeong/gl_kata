import csv

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import numpy as np
import moderngl as mg
from glm import *


def readshader(path):
    with open(path, "r") as fp:
        return fp.read()


def readvbo(path):
    with open(path, "r") as f:
        reader = csv.reader(f)
        data = np.array([row for row in reader])
        pos0 = data[1:, 1:4]
        return np.hstack((pos0)).astype(np.float32).flatten()


def readibo(path):
    with open(path, "r") as f:
        content = f.read()

    indices = []
    for line in content.splitlines():
        try:
            indices.append(int(line))
        except ValueError:
            pass
    return np.array(indices).astype(np.int32)


class Material(object):
    def __init__(self, gl, vspath, fspath):
        super(Material, self).__init__()
        vs, fs = readshader(vspath), readshader(fspath)
        self.program = gl.program(vertex_shader=vs, fragment_shader=fs)

    def get(self):
        return self.program


class Mesh(object):
    def __init__(self, gl, vbopath, ibopath, body_program):
        super(Mesh, self).__init__()

        self.gl = gl
        self.init(gl, vbopath, ibopath, body_program)

    def init(self, gl, vbopath, ibopath, body_program):
        vertices, indices = readvbo(vbopath), readibo(ibopath)
        vbo, ibo = gl.buffer(vertices), gl.buffer(indices)
        content = [(vbo, "3f", "in_pos_0")]
        self.vao = gl.vertex_array(body_program.get(), content, ibo, skip_errors=True)

    def render(self):
        self.vao.render()


class Minotaur(object):
    def __init__(self, gl):
        super(Minotaur, self).__init__()
        self.gl = gl

        vbo, ibo = "./mesh/minotaur_body.vbo", "./mesh/minotaur_body.ibo"
        vs, fs = "./gl/vs.glsl", "./gl/fs.glsl"
        body_prog = Material(gl, vs, fs)
        self.body = Mesh(gl, vbo, ibo, body_prog)

    def render(self):
        self.body.render()


class Client(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(Client, self).__init__()

        self.setMinimumSize(1024, 1024)
        self.setMaximumSize(1024, 1024)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def initializeGL(self):
        self.gl = mg.create_context()

        self.campos = vec4(0.0, 0.0, -5.0, 1.0)
        data = [self.campos]
        self.client_const = self.gl.buffer(reserve=4 * len(data))
        self.client_const.bind_to_storage_buffer(0)

        self.minotaur = Minotaur(self.gl)

        vs, fs = readshader("./gl/vs.glsl"), readshader("./gl/fs.glsl")
        program = self.gl.program(vertex_shader=vs, fragment_shader=fs)
        vb = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0], dtype=np.float32)
        ib = np.array([0, 1, 2, 2, 1, 3], dtype=np.int32)
        vbo, ibo = self.gl.buffer(vb), self.gl.buffer(ib)
        content = [(vbo, "2f", "in_pos")]
        self.quad = self.gl.vertex_array(program, content, ibo, skip_errors=True)

    def paintGL(self):
        # self.minotaur.render()
        self.quad.render()
        # self.update()


def main():
    app = QtWidgets.QApplication([])
    client = Client()
    client.show()
    app.exec()


if __name__ == "__main__":
    main()
