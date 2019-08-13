from threading import Thread

import numpy as np
import moderngl as mg
import glfw
import webview as wv
from jinja2 import Template

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def read(path):
    with open(path, "r") as fp:
        return fp.read()


class GLFWWindow(Thread):
    should_recompile = False

    def __init__(self):
        super(GLFWWindow, self).__init__()

    def set_should_recompile(self, should):
        self.should_recompile = should

    def recompile(self):
        try:
            for vao in self.vaos:
                vao = None

            self.vaos.clear()

            print("Cleared vaos")

        except Exception as e:
            print(e)

        try:
            program = self.gl.program(
                vertex_shader=read("./gl/default_vs.glsl"),
                fragment_shader=read("./gl/default_fs.glsl"),
            )
            vao = self.gl.vertex_array(program, self.vbo, self.ibo)
            self.vaos.append(vao)

            print("Recompiled program")

        except Exception as e:
            print(e)

    def init_render(self):
        self.gl = mg.create_context()
        gl = self.gl
        self.vaos = []

        self.vbo = [
            (
                gl.buffer(
                    np.array([-1.0, -1.0, -1.0, +1.0, +1.0, -1.0, +1.0, +1.0])
                    .astype(np.float32)
                    .tobytes()
                ),
                "2f",
                "in_pos",
            )
        ]
        self.ibo = gl.buffer(np.array([0, 1, 2, 2, 1, 3]).astype(np.int32).tobytes())

        self.recompile()

        handler = FileSystemEventHandler()
        handler.on_modified = lambda e: self.set_should_recompile(True)

        observer = Observer()
        observer.schedule(handler, "./gl/", True)
        observer.start()

    def render(self):
        for vao in self.vaos:
            vao.render()

    def run(self):
        glfw.init()
        width, height = 400, 400
        title = "GLFW"
        window = glfw.create_window(width, height, title, None, None)
        glfw.make_context_current(window)

        self.init_render()

        while not glfw.window_should_close(window):
            if self.should_recompile:
                self.should_recompile = False
                self.recompile()
            self.render()

            glfw.swap_buffers(window)
            glfw.poll_events()


class JSAPI(object):
    def __init__(self):
        super(JSAPI, self).__init__()

    def send_to_console(self, params):
        print("AAA")
        print(params)
        return params


def main():
    # glfw_window = GLFWWindow()
    # glfw_window.start()

    # py webview requires to be started from main thread
    wv.create_window(
        "Web View",
        html=Template(read("./html/index.html")).render(
            {
                "path": "http://localhost:8080/zzz92229ddd/html/",
                "default_vs_glsl": read("./gl/default_vs.glsl"),
                "default_fs_glsl": read("./gl/default_fs.glsl"),
            }
        ),
        js_api=JSAPI(),
        text_select=True,
        width=400,
        height=400,
    )
    wv.start()


if __name__ == "__main__":
    main()
