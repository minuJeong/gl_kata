import time
import math
from threading import Thread
from queue import Queue
import logging
import csv

import ctypes as c
import OpenGL.GL as gl
import glfw
import glm as m
import numpy as np


logging.basicConfig(format="[%(asctime)s] %(message)s")
log = logging.getLogger("Root")
log.setLevel(logging.DEBUG)
handler_file = logging.FileHandler("C:/log/_log.txt")
log.addHandler(handler_file)


def readshader(path):
    with open(path, "r") as f:
        return f.read()


def readvb(path):
    with open(path, "r") as f:
        reader = csv.reader(f)
        data = np.array([row for row in reader])
        pos0 = data[1:, 1:4]
        return np.hstack([pos0]).astype(np.float32).flatten()


def readib(path):
    with open(path, "r") as f:
        content = f.read()

    indices = []
    for line in content.splitlines():
        try:
            indices.append(int(line))
        except ValueError:
            pass
    return np.array(indices).astype(np.int32)


class Mesh(object):
    program = None
    vao = None
    len_indices = 0

    def __init__(self, vs_src, fs_src):
        super(Mesh, self).__init__()

        # compile shaders
        self.compile(vs_src, fs_src)

    def uniform(self, uname, uvalue):
        try:
            uloc = gl.glGetUniformLocation(self.program, uname)

            if isinstance(uvalue, (m.mat4)):
                gl.glUniformMatrix4fv(uloc, 1, gl.GL_FALSE, m.value_ptr(uvalue))
            elif isinstance(uvalue, (float)):
                gl.glUniform1f(uloc, 1, gl.GL_FALSE, m.value_ptr(uvalue))
            # ... add more types to use

        except Exception as e:
            log.info("[Mesh] Error in uniform")
            log.debug(e)

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
        T = glfw.get_time()

        if self.program is not None:
            gl.glUseProgram(self.program)

            M = m.translate(m.mat4(1.0), m.vec3(0.0, -0.7, 0.0))
            campos = m.vec3(math.cos(T) * 2.0, 0.0, math.sin(T) * 2.0)
            V = m.lookAt(campos, m.vec3(0.0), m.vec3(0.0, 1.0, 0.0))
            P = m.perspective(m.radians(74.0), 1.0, 0.001, 100.0)

            u_MVP = P * V * M
            self.uniform("u_MVP", u_MVP)

        if self.vao is not None:
            gl.glBindVertexArray(self.vao)
            gl.glDrawElements(
                gl.GL_TRIANGLES, self.len_indices, gl.GL_UNSIGNED_SHORT, None
            )


class AlbericBordeleaux(Mesh):
    def __init__(self):

        dirname = "D:/Local/Python/gl_kata/2020/1/pyside2+pyopengl"
        super(AlbericBordeleaux, self).__init__(
            readshader("{}/gl/vs_ab.glsl".format(dirname)),
            readshader("{}/gl/fs_ab.glsl".format(dirname)),
        )

        # build vertex arrays..
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        vbpath = ("{}/mesh/alberic_bordeleaux.vbo".format(dirname))
        ibpath = ("{}/mesh/alberic_bordeleaux.ibo".format(dirname))
        vertices, indices = readvb(vbpath), readib(ibpath)
        vbo, ibo = gl.glGenBuffers(2)

        in_pos = gl.glGetAttribLocation(self.program, "in_pos")
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            (c.c_float * len(vertices))(*vertices),
            gl.GL_STATIC_DRAW,
        )
        gl.glVertexAttribPointer(in_pos, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glEnableVertexAttribArray(in_pos)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        # build index buffer..
        self.len_indices = len(indices)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ibo)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER,
            (c.c_ushort * self.len_indices)(*indices),
            gl.GL_STATIC_DRAW,
        )


class Client(Thread):
    def on_key(self, window, key, scan, act, mods):
        # hit space to close window
        if key == glfw.KEY_SPACE:
            log.info("key spacebar hit to closing..")
            glfw.set_window_should_close(self.window, glfw.TRUE)

    def __init__(self, queue=None):
        super(Client, self).__init__()
        self.queue = queue or Queue()

    def start(self):

        # init window/gl
        glfw.init()
        self.window = glfw.create_window(1024, 1024, "Render Window Test", None, None)
        glfw.make_context_current(self.window)

        # init client
        self.init()

        glfw.set_key_callback(self.window, self.on_key)

        # render loop
        try:
            while not glfw.window_should_close(self.window):
                glfw.poll_events()
                glfw.swap_buffers(self.window)
                self.render()

        except Exception as e:
            log.debug(e)

        glfw.terminate()

    def init(self):
        # check device OpenGL version
        self.albericborderleaux = AlbericBordeleaux()

    def render(self):
        # clear frame buffer..
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # render config
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthMask(gl.GL_TRUE)
        gl.glDepthFunc(gl.GL_LESS)

        self.albericborderleaux.render()


def main():
    queue = Queue()
    client_thread = Client(queue)
    client_thread.start()


if __name__ == "__main__":
    main()

else:
    print(__name__)
