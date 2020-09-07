import glfw
import numpy as np
import moderngl as mg
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Client(object):
    def __init__(self, window):
        super().__init__()
        self.window = window

        self.gl = mg.create_context()
        self.compile()

        def on_mod(e):
            self._should_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_mod

        observer = Observer()
        observer.schedule(handler, "./gl/", True)
        observer.start()

    def compile(self):
        self._should_compile = False

        print("compiling..")

        try:
            VS, FS = open("./gl/quad.vs").read(), open("./gl/quad.fs").read()
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            vertices = self.gl.buffer(
                np.array(
                    [
                        [-1.0, -1.0, 0.0, 1.0],
                        [-1.0, +1.0, 0.0, 1.0],
                        [+1.0, -1.0, 0.0, 1.0],
                        [+1.0, +1.0, 0.0, 1.0],
                    ],
                    dtype=np.float32,
                )
            )
            vertices_content = [(vertices, "4f", "in_pos")]
            indices = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))
            self.quad = self.gl.vertex_array(program, vertices_content, indices)

            print("shaders compiled")

        except Exception as e:
            print(e)

    def update(self):
        if self._should_compile:
            self.compile()
            return

        self.gl.clear()
        self.quad.render()


def main():
    assert glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(512, 512, "", None, None)
    glfw.make_context_current(window)
    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.swap_buffers(window)
        glfw.poll_events()
        client.update()


if __name__ == "__main__":
    main()
