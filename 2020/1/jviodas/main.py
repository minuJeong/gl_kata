import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders as shaders
from PySide2 import QtWidgets


def read(path):
    with open(path, "r") as f:
        return f.read()


class GL():
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
        self.program = shaders.compileProgram(
            shaders.compileShader(read("./gl/vs.glsl"), GL_VERTEX_SHADER),
            shaders.compileShader(read("./gl/fs.glsl"), GL_FRAGMENT_SHADER)
        )

        # build vertex arrays..
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # build vertex buffer..
        self.vertices = np.array([-1, -1, +1, -1, -1, +1, +1, +1], dtype=np.float32)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        in_pos = glGetAttribLocation(self.program, "in_pos")
        is_binding_attrib = False
        if in_pos > 0:
            is_binding_attrib = True
            glEnableVertexAttribArray(in_pos)
        glBufferData(GL_ARRAY_BUFFER, len(self.vertices) * 4, self.vertices, GL_STATIC_DRAW)
        if is_binding_attrib:
            glDisableVertexAttribArray(in_pos)

        # build index buffer..
        self.indices = np.array([0, 1, 2, 2, 1, 3], dtype=np.int32)
        self.ibo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ARRAY_BUFFER, len(self.indices) * 4, self.indices, GL_STATIC_DRAW)

        # release buffers (important!)
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
