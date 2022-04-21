import sys

import mouse
import keyboard
from glm import cos
import glfw
import moderngl as mg
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from deltatime import Time
from mesh import Mesh


class Client:
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.gl = mg.create_context(require=460)

        self.quad = None
        self.step = None

        self.compile_shaders()

        ob = Observer()
        handler = FileSystemEventHandler()
        handler.on_modified = lambda e: self.invalidate_shader()
        ob.schedule(handler, "./gl", True)
        ob.start()

    def invalidate_shader(self):
        self._should_compile_shaders = True

    def compile_shaders(self):
        self._should_compile_shaders = False

        try:
            program = Mesh.get_program_path(self.gl, "./gl/quad.vs", "./gl/quad.fs")
            vertex_array = Mesh.get_vertex_array(self.gl, program)
            self.quad = Mesh(self.gl, vertex_array)
            self.uniform("u_resolution", glfw.get_window_size(self.window))

            self.field = self.gl.buffer(reserve=128 * 128 * 128)
            self.field.bind_to_storage_buffer(0)
            self.step = self.gl.compute_shader(open("./gl/step.cs").read())

            print("compiled shaders")

        except Exception as e:
            print(e)

    def uniform(self, uname, uvalue):
        for p in [self.quad, self.step]:
            if not p:
                continue

            if hasattr(p, "uniform"):
                p.uniform(uname, uvalue)
                continue

            if uname not in p:
                continue

            p[uname].value = uvalue

    def update(self):
        if self._should_compile_shaders:
            self.compile_shaders()

        txt = f"{Time.elapsed_frames}, {Time.framerate:.2f}"
        glfw.set_window_title(self.window, txt)

        self.uniform("u_time", Time.time)

        self.step.run(1, 1, 1)
        self.quad.render()


def main():
    assert glfw.init()

    WIDTH, HEIGHT = 1920, 1080
    WIDTH, HEIGHT = 1280, 720
    WIDTH, HEIGHT = 400, 400
    
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, "window", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        Time.next_frame()
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
