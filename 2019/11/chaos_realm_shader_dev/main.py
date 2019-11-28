import glfw
import numpy as np
import moderngl as mg
from glm import *

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def readshader(path):
    with open(path, "r") as fp:
        return fp.read()


def readbytes(path):
    with open(path, "rb") as fp:
        return fp.read()


class Mesh(object):
    def __init__(self, gl, vbib, vsfs):
        self.program = gl.program(
            vertex_shader=readshader(vsfs[0]), fragment_shader=readshader(vsfs[1])
        )

        self.vb = readbytes(vbib[0])
        self.ib = readbytes(vbib[1])

    def uniform(self, n, v):
        if n not in self.program:
            return

        u = self.program[n]
        if isinstance(v, (vec3, vec4, mat4)):
            u.write(bytes(v))
        else:
            u.value = v


class ScreenMesh(Mesh):
    def __init__(self, gl, vbib, vsfs):
        super(ScreenMesh, self).__init__(gl, vbib, vsfs)
        vb_content = [(gl.buffer(self.vb), "4f 2f", "in_pos", "in_texcoord",)]
        self.vao = gl.vertex_array(
            self.program, vb_content, gl.buffer(self.ib), skip_errors=True,
        )
        self.render = self.vao.render


class Scene(object):
    def on_modified(self, e):
        self.should_compile = True

    def __init__(self, window, width, height):
        super(Scene, self).__init__()

        self.window = window
        self.width, self.height = width, height

        print("initializing gpu..")
        self.gl = mg.create_context()

        self.compile()

        h = FileSystemEventHandler()
        h.on_modified = self.on_modified
        o = Observer()
        o.schedule(h, "./gl/", True)
        o.start()

    def compile(self):
        self.should_compile = False
        self.meshes = []
        try:
            self.camera_pos = vec3(-5.0, 5.0, -5.0)
            self.meshes.append(
                ScreenMesh(
                    self.gl,
                    ("./mesh/screen_mesh.vb", "./mesh/screen_mesh.ib"),
                    ("./gl/vs_screen.glsl", "./gl/fs_screen.glsl"),
                )
            )

            self.uniform("u_aspect", self.width / self.height)
            print("compiled Draw")

        except Exception as e:
            print(e)

    def uniform(self, n, v):
        for mesh in self.meshes:
            mesh.uniform(n, v)

    def render(self):
        if self.should_compile:
            self.compile()
            return

        self.uniform("u_time", glfw.get_time())
        self.uniform("u_camerapos", self.camera_pos)

        for mesh in self.meshes:
            mesh.render()


def main():
    width, height = 1920, 1080
    title = "CHAOS REALM BOUNDARY"

    print("initializing glfw..")

    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(width, height, title, None, None)
    glfw.make_context_current(window)
    scene = Scene(window, width, height)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        scene.render()
        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
