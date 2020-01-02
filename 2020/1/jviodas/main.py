import ctypes as c
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders as shaders
from PySide2 import QtWidgets


def read(path):
    with open(path, "r") as f:
        return f.read()


class GL:
    def __init__(self):
        super(GL, self).__init__()


class RenderWidget(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(RenderWidget, self).__init__()

        # set current GPU context to widget
        self.makeCurrent()

    def initializeGL(self):
        # version check
        version = glGetString(GL_VERSION)
        sl_version = glGetString(GL_SHADING_LANGUAGE_VERSION)
        extensions = glGetString(GL_EXTENSIONS)
        print(f"GL Version: {version}, GLSL Version: {sl_version}")

        # compile shaders
        vs = glCreateShader(GL_VERTEX_SHADER)
        vs_src = read("./gl/vs.glsl")
        glShaderSource(vs, vs_src)
        glCompileShader(vs)

        fs = glCreateShader(GL_FRAGMENT_SHADER)
        fs_src = read("./gl/fs.glsl")
        glShaderSource(fs, fs_src)
        glCompileShader(fs)

        self.program = glCreateProgram()
        glAttachShader(self.program, vs)
        glAttachShader(self.program, fs)
        glLinkProgram(self.program)

        # build vertex arrays..
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # build vertex buffer..
        self.vertices = [-1, -1, +1, -1, -1, +1, +1, +1]
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        in_pos = glGetAttribLocation(self.program, "in_pos")
        is_binding_attrib = False
        if in_pos > 0:
            is_binding_attrib = True
            glEnableVertexAttribArray(in_pos)
            glVertexAttribPointer(in_pos, 2, GL_FLOAT, GL_FALSE, 0.0, None)
        glBufferData(
            GL_ARRAY_BUFFER,
            (c.c_float * len(self.vertices))(*self.vertices),
            GL_STATIC_DRAW,
        )
        if is_binding_attrib:
            glDisableVertexAttribArray(in_pos)

        # build index buffer..
        self.indices = np.array([0, 1, 2, 2, 1, 3], dtype=np.int32)
        self.ibo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.ibo)
        glBufferData(
            GL_ARRAY_BUFFER,
            (c.c_int32 * len(self.indices))(*self.indices),
            GL_STATIC_DRAW,
        )

        # release (important!)
        glDeleteShader(vs)
        glDeleteShader(fs)
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def paintGL(self):
        # clear frame buffer..
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # render vertex array using program..
        glUseProgram(self.program)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 3)

        # release..
        glBindVertexArray(0)
        glUseProgram(0)

        self.update()


def main():
    app = QtWidgets.QApplication([])
    render = RenderWidget()
    render.show()
    app.exec_()


if __name__ == "__main__":
    main()

else:
    print(__name__)
