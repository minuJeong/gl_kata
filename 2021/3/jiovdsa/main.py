import moderngl as mg
import numpy as np
import glfw
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Handler(FileSystemEventHandler):
    client = None

    def __init__(self, client):
        super().__init__()
        self.client = client

    def on_modified(self, e):
        self.client.should_compile = True


class Client(object):
    window = None
    gl = None
    should_compile = False

    def __init__(self, window):
        super().__init__()

        self.window = window
        self.gl = mg.create_context()

        self.compile()

        observer = Observer()
        observer.schedule(Handler(self), "./gl", True)
        observer.start()

    def compile(self):
        VS, FS = open("./gl/quad.vs").read(), open("./gl/quad.fs").read()
        self.quad = self.gl.vertex_array(
            self.gl.program(vertex_shader=VS, fragment_shader=FS),
            [
                (
                    self.gl.buffer(
                        np.array(
                            [
                                *vec4(-1.0, -1.0, 0.0, 1.0),
                                *vec4(+1.0, -1.0, 0.0, 1.0),
                                *vec4(-1.0, +1.0, 0.0, 1.0),
                                *vec4(+1.0, +1.0, 0.0, 1.0),
                            ],
                            dtype=np.float32,
                        )
                    ),
                    "4f",
                    "in_pos",
                )
            ],
            self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32)),
            skip_errors=True,
        )

    def update(self):
        if self.should_compile:
            self.should_compile = False
            try:
                self.compile()
                print("compiled")

            except Exception as e:
                print(e)

            return

        if "u_time" in self.quad.program:
            self.quad.program["u_time"] = glfw.get_time()
        self.quad.render()


def main():
    assert glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(800, 800, "Render View", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)

        client.update()


if __name__ == "__main__":
    main()
