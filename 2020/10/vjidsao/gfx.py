import numpy as np
import moderngl as mg
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class GFX(object):
    def init(self):
        self.gl = mg.create_context()

        self.compile_shaders()

        def on_mod(e):
            self.should_compile_shaders = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_mod
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

    def compile_shaders(self):
        self.should_compile_shaders = False
        try:
            VS, FS = open("./gl/quad.vs").read(), open("./gl/quad.fs").read()
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            vertices = np.array(
                [
                    *vec4(-1.0, -1.0, 0.0, 1.0),
                    *vec4(-1.0, +1.0, 0.0, 1.0),
                    *vec4(+1.0, -1.0, 0.0, 1.0),
                    *vec4(1.0, 1.0, 0.0, 1.0),
                ],
                dtype=np.float32,
            )
            vbo = self.gl.buffer(vertices)
            ibo = self.gl.buffer(np.array((0, 1, 2, 2, 1, 3), dtype=np.int32))
            self.vao = self.gl.vertex_array(program, [(vbo, "4f", "in_pos")], ibo)

            print("compiled shaders")

        except Exception as e:
            print(e)

    def uniform(self):
        pass

    def tick(self, elapsed_time, delta_time):
        # skip a frame when compiling shaders
        if self.should_compile_shaders:
            self.compile_shaders()
            return

        self.vao.render()


if __name__ == "__main__":
    from main import main

    main()
