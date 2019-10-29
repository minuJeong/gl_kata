from glm import *
import glfw
import moderngl as mg
import numpy as np

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from util import Util
from mesh import Mesh


class Scene(object):
    def __init__(self, width, height):
        super(Scene, self).__init__()
        self.width, self.height = width, height
        self.meshes = []

        self.gl = mg.create_context()

        cs = "./gl/screen/cs_generate_screen.glsl"
        vs, fs = "./gl/screen/vs_screen.glsl", "./gl/screen/fs_screen.glsl"
        mesh = Mesh(cs, vs, fs)
        self.add_mesh(mesh)
        self.compile()

        def on_mod(e):
            self.should_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_mod
        observer = Observer()
        observer.schedule(handler, "./gl/")
        observer.start()

    def add_mesh(self, mesh):
        self.meshes.append(mesh)

    def remove_mesh(self, mesh):
        if mesh in self.meshes:
            self.meshes.remove(mesh)

    def compile(self):
        self.should_compile = False

        try:
            for mesh in self.meshes:
                mesh.compile(self.gl)

            print("compiled")

        except Exception as e:
            print(e)

    def render(self):
        if self.should_compile:
            self.compile()

        self.gl.clear(depth=100.0)

        for mesh in self.meshes:
            mesh.render()

    def on_resize(self, window, width, height):
        self.gl.viewport = (0, 0, width, height)
        self.width, self.height = width, height


def main():
    glfw.init()

    width, height = 500, 500

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(width, height, "hello", None, None)
    glfw.make_context_current(window)

    scene = Scene(width, height)
    glfw.set_window_size_callback(window, scene.on_resize)

    while not glfw.window_should_close(window):
        scene.render()
        glfw.swap_buffers(window)
        glfw.poll_events()


if __name__ == "__main__":
    main()
