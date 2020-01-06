import os
from threading import Thread

import ctypes as c
import OpenGL.GL as gl
import glfw


def read(path):
    with open(path, "r") as f:
        return f.read()


class Mesh(object):
    program = None
    vao = None
    len_indices = 0

    def __init__(self):
        super(Mesh, self).__init__()

    def compile(self, vs_src, fs_src):
        vs = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(vs, vs_src)
        gl.glCompileShader(vs)

        fs = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fs, fs_src)
        gl.glCompileShader(fs)

        self.program = gl.glCreateProgram()
        gl.glAttachShader(self.program, vs)
        gl.glAttachShader(self.program, fs)
        gl.glLinkProgram(self.program)
        gl.glDeleteShader(vs)
        gl.glDeleteShader(fs)

        return self.program

    def render(self):
        if self.program is not None:
            gl.glUseProgram(self.program)

        if self.vao is not None:
            gl.glBindVertexArray(self.vao)

        if self.len_indices > 0:
            gl.glDrawElements(gl.GL_TRIANGLES, self.len_indices, gl.GL_UNSIGNED_SHORT, None)


class Quad(Mesh):
    def __init__(self, vs_src, fs_src):
        super(Quad, self).__init__()

        # compile shaders
        self.compile(vs_src, fs_src)

        # build vertex arrays..
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        # build vertex buffer..
        vertices = [-1, -1, +1, -1, -1, +1, +1, +1]
        vbo = gl.glGenBuffers(1)
        in_pos = gl.glGetAttribLocation(self.program, "in_pos")
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            (c.c_float * len(vertices))(*vertices),
            gl.GL_STATIC_DRAW,
        )
        gl.glVertexAttribPointer(in_pos, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glEnableVertexAttribArray(in_pos)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        # build index buffer..
        indices = [0, 1, 2, 1, 2, 3]
        self.len_indices = len(indices)
        ibo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ibo)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER,
            (c.c_ushort * self.len_indices)(*indices),
            gl.GL_STATIC_DRAW,
        )


class RenderLoop(object):
    @staticmethod
    def on_key(window, key, scan, act, mods):
        # hit space to close window
        if key == glfw.KEY_SPACE:
            glfw.set_window_should_close(RenderLoop.window, glfw.TRUE)

    @staticmethod
    def renderloop():
        # init window/gl
        init = glfw.init()
        print(init)

        glfw.window_hint(glfw.FLOATING, glfw.TRUE)
        RenderLoop.window = glfw.create_window(512, 512, "", None, None)
        glfw.make_context_current(RenderLoop.window)
        RenderLoop.init()

        glfw.set_key_callback(RenderLoop.window, RenderLoop.on_key)

        # render loop
        while not glfw.window_should_close(RenderLoop.window):
            glfw.poll_events()
            glfw.swap_buffers(RenderLoop.window)
            RenderLoop.render()

        print("exit(0);")

    @staticmethod
    def init():
        # check device OpenGL version
        version = gl.glGetString(gl.GL_VERSION)
        sl_version = gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)
        print("GL Version: {}, GLSL Version: {}".format(version, sl_version))

        # generate quad
        dirname = os.path.dirname(os.path.abspath("__file__"))
        vs_src = read("{}/gl/vs.glsl".format(dirname))
        fs_src = read("{}/gl/fs.glsl".format(dirname))
        RenderLoop.quad = Quad(vs_src, fs_src)

    @staticmethod
    def render():
        # clear frame buffer..
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        RenderLoop.quad.render()


def main():
    t = Thread(target=RenderLoop.renderloop)
    t.start()


if __name__ == "__main__":
    main()

else:
    print(__name__)
