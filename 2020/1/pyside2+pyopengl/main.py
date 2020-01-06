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
            try:
                gl.glUseProgram(self.program)

                u_MVP_loc = gl.glGetUniformLocation(self.program, "u_MVP")
                M = m.translate(m.mat4(1.0), m.vec3(0.0, -0.7, 0.0))
                campos = m.vec3(math.cos(T) * 2.0, 0.0, math.sin(T) * 2.0)
                V = m.lookAt(campos, m.vec3(0.0), m.vec3(0.0, 1.0, 0.0))
                P = m.perspective(m.radians(74.0), 1.0, 0.001, 100.0)
                u_MVP = P * V * M
                gl.glUniformMatrix4fv(u_MVP_loc, 1, gl.GL_FALSE, m.value_ptr(u_MVP))

            except Exception as e:
                log.info("[Render] Error in program")
                log.debug(e)

        if self.vao is not None:
            try:
                gl.glBindVertexArray(self.vao)
                gl.glDrawElements(
                    gl.GL_TRIANGLES, self.len_indices, gl.GL_UNSIGNED_SHORT, None
                )

            except Exception as e:
                log.info("[Render] Error in draw")
                log.debug(e)


# NOT USED
class Quad(Mesh):
    def __init__(self, vs_src, fs_src):
        super(Quad, self).__init__(vs_src, fs_src)

        # build vertex arrays..
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        # build vertex buffer..
        vertices = [-1, -1, +1, -1, -1, +1, +1, +1]
        vbo, ibo = gl.glGenBuffers(2)

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
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ibo)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER,
            (c.c_ushort * self.len_indices)(*indices),
            gl.GL_STATIC_DRAW,
        )


class AlbericBordeleaux(Mesh):
    def __init__(self):
        super(AlbericBordeleaux, self).__init__(
            readshader("D:/Local/Python/gl_kata/2020/1/pyside2+pyopengl/gl/vs_ab.glsl"),
            readshader("D:/Local/Python/gl_kata/2020/1/pyside2+pyopengl/gl/fs_ab.glsl"),
        )

        # build vertex arrays..
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        vbpath = (
            "D:/Local/Python/~2019/~12/nsight_mesh_extract/mesh/alberic_bordeleaux.vbo"
        )
        ibpath = (
            "D:/Local/Python/~2019/~12/nsight_mesh_extract/mesh/alberic_bordeleaux.ibo"
        )
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


class Client(object):
    @staticmethod
    def on_key(window, key, scan, act, mods):
        # hit space to close window
        if key == glfw.KEY_SPACE:
            log.info("key spacebar hit to closing..")
            glfw.set_window_should_close(Client.window, glfw.TRUE)

    @staticmethod
    def renderloop(queue=None):
        Client.queue = queue or Queue()

        # init window/gl
        glfw.init()
        glfw.window_hint(glfw.FLOATING, glfw.TRUE)
        Client.window = glfw.create_window(1024, 1024, "", None, None)
        glfw.make_context_current(Client.window)

        # init client
        Client.init()

        glfw.set_key_callback(Client.window, Client.on_key)

        # render loop
        starttime = time.time()
        while (
            not glfw.window_should_close(Client.window)
            or starttime + 10.0 < time.time()
        ):
            glfw.poll_events()
            glfw.swap_buffers(Client.window)
            Client.render()

    @staticmethod
    def init():
        # check device OpenGL version
        Client.albericborderleaux = AlbericBordeleaux()

    @staticmethod
    def render():
        # clear frame buffer..
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # render config
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthMask(gl.GL_TRUE)
        gl.glDepthFunc(gl.GL_LESS)

        Client.albericborderleaux.render()


def main():
    queue = Queue()
    t1 = Thread(target=Client.renderloop, args=(queue,))
    t1.start()


if __name__ == "__main__":
    main()

else:
    print(__name__)
