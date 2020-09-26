import struct

import glfw
import moderngl as mg
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Client(object):
    def __init__(self, window):
        super().__init__()
        self.start()

    def start(self):
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
        try:
            VS, FS = open("./gl/quad.vs").read(), open("./gl/quad.fs").read()
            self.program = self.gl.program(vertex_shader=VS, fragment_shader=FS)

            vertex_buffer = self.gl.buffer(
                struct.pack(
                    "16f",
                    -1.0,
                    -1.0,
                    0.0,
                    1.0,
                    +1.0,
                    -1.0,
                    0.0,
                    1.0,
                    -1.0,
                    +1.0,
                    0.0,
                    1.0,
                    +1.0,
                    +1.0,
                    0.0,
                    1.0,
                )
            )
            index_buffer = self.gl.buffer(struct.pack("6i", 0, 1, 2, 2, 1, 3))
            self.quad = self.gl.vertex_array(
                self.program,
                [(vertex_buffer, "4f", "in_pos")],
                index_buffer,
                skip_errors=True,
            )
            self.uniform({"u_resolution": (800, 600)})

            print("compiled")

        except Exception as e:
            print(e)

    def uniform(self, data: dict):
        for key, value in data.items():
            if key not in self.program:
                continue

            self.program[key] = value

    def update(self):
        if self._should_compile:
            self.compile()

        self.uniform({"u_time": glfw.get_time()})
        self.quad.render()


def main():
    assert glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    win = glfw.create_window(800, 600, "", None, None)
    glfw.make_context_current(win)

    client = Client(win)

    while not glfw.window_should_close(win):
        glfw.poll_events()
        glfw.swap_buffers(win)
        client.update()


if __name__ == "__main__":
    main()
