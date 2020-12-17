import glfw
import numpy as np
import moderngl as mg
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from glm import vec4

from const import WIDTH, HEIGHT, CHANNELS, BYTE_SIZE


class Client(object):
    window = None
    gl = None
    cs_init = None
    cs_update = None
    quad = None

    def __init__(self, window):
        super().__init__()

        self.window = window
        self.gl = mg.create_context(require=460)
        self.should_compile = True

        class Handler(FileSystemEventHandler):
            def __init__(self, client):
                super().__init__()
                self.client = client

            def on_modified(self, e):
                self.client.should_compile = True

        handler = Handler(self)
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

    def compile(self):
        pass

    def render(self):
        pass

    def uniform(self, uname, uvalue):
        for p in [self.cs_init, self.cs_update, self.quad.program]:
            if uname not in p:
                continue

            p[uname] = uvalue

    def update(self):
        if self.should_compile:
            self.compile()
            return

        self.uniform("u_time", glfw.get_time())
        self.render()


class MyClient(Client):
    swap = False

    def compile(self):
        self.should_compile = False
        try:
            VS, FS = open("./gl/quad.vs").read(), open("./gl/quad.fs").read()
            CS_INIT, CS_UPDATE = (
                open("./gl/compute_init.glsl").read(),
                open("./gl/compute_update.glsl").read(),
            )

            self.cs_init = self.gl.compute_shader(CS_INIT)
            self.cs_update = self.gl.compute_shader(CS_UPDATE)

            buffer_size = WIDTH * HEIGHT * (4 + CHANNELS) * BYTE_SIZE
            self.buffer_0 = self.gl.buffer(reserve=buffer_size)
            self.buffer_1 = self.gl.buffer(reserve=buffer_size)

            self.buffer_0.bind_to_storage_buffer(0)
            self.buffer_1.bind_to_storage_buffer(1)
            self.swap = True

            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            vb = self.gl.buffer(
                np.array(
                    [
                        *vec4(-1.0, -1.0, 0.0, 1.0),
                        *vec4(+1.0, -1.0, 0.0, 1.0),
                        *vec4(-1.0, +1.0, 0.0, 1.0),
                        *vec4(+1.0, +1.0, 0.0, 1.0),
                    ],
                    dtype=np.float32,
                )
            )
            ib = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))
            self.quad = self.gl.vertex_array(program, [(vb, "4f", "in_pos")], ib)

            self.uniform("u_resolution", (WIDTH, HEIGHT))

            self.GX, self.GY, self.GZ = WIDTH // 8, HEIGHT // 8, 1
            self.cs_init.run(self.GX, self.GY, self.GZ)

            print("compiled")

        except Exception as e:
            print(e)

    def render(self):
        if self.swap:
            self.buffer_0.bind_to_storage_buffer(0)
            self.buffer_1.bind_to_storage_buffer(1)
        else:
            self.buffer_0.bind_to_storage_buffer(1)
            self.buffer_1.bind_to_storage_buffer(0)
        self.swap = not self.swap

        self.cs_update.run(self.GX, self.GY, self.GZ)
        self.quad.render()


if __name__ == "__main__":
    from main_2 import main

    main()
