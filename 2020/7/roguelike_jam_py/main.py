import glfw
import numpy as np
import moderngl as mg
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Client:
    def __init__(self, window):
        super().__init__()
        self.window = window

        self.gl = mg.create_context()
        self.reload()

        def on_modified(e):
            self.should_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_modified
        observer = Observer(handler, "./gl/", True)
        observer.start()

    def reload(self):
        try:
            vs, fs = open("./gl/quad.vs").read(), open("./gl/quad.fs").read()
            program = self.gl.program(vertex_shader=vs, fragment_shader=fs)
            vertices = np.array(
                [[-1, -1, 0, 1], [-1, +1, 0, 1], [+1, -1, 0, 1], [+1, +1, 0, 1]],
                dtype=np.float32,
            )
            vertices_buffer = self.gl.buffer(vertices)
            indices = np.array([0, 1, 2, 2, 1, 3], dtype=np.int32)
            indices_buffer = self.gl.buffer(indices)
            self.quad = self.gl.vertex_array(
                program, [(vertices_buffer, "4f", "in_pos")], indices_buffer
            )

        except Exception as e:
            print(e)

    def update(self):
        if self.should_compile:
            self.reload()
            return

        self.quad.render()


def main():
    glfw.init()
    window = glfw.create_window(512, 512, "-", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.swap_buffers(window)
        glfw.poll_events()
        client.update()


if __name__ == "__main__":
    main()
