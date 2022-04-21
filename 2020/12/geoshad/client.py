import numpy as np
import moderngl as mg
from glm import vec4
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from const import WIDTH, HEIGHT


class Client(object):
    _should_compile = False
    vao = None

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
        observer.schedule(handler, "./gl", True)
        observer.start()

    def compile(self):
        self._should_compile = False

        try:
            VS, FS = open("./gl/vert.glsl").read(), open("./gl/frag.glsl").read()
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            verts = [
                *vec4(-1.0, -1.0, 0.0, 1.0),
                *vec4(+1.0, -1.0, 0.0, 1.0),
                *vec4(-1.0, +1.0, 0.0, 1.0),
                *vec4(+1.0, +1.0, 0.0, 1.0),
            ]
            vb = self.gl.buffer(np.array(verts, dtype=np.float32))
            ib = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))
            self.vao = self.gl.vertex_array(program, [(vb, "4f", "in_pos")], ib)

            self.uniform("u_resolution", (WIDTH, HEIGHT))

            print("compiled")

        except Exception as e:
            print(e)

    def uniform(self, uname, uvalue):
        if uname not in self.vao.program:
            return

        self.vao.program[uname] = uvalue

    def update(self):
        if self._should_compile:
            self.compile()
            return

        self.vao.render()


if __name__ == "__main__":
    from main import main

    main()
