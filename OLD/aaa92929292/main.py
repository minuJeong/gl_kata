
import numpy as np
import moderngl as mg
import glfw

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


WIDTH, HEIGHT = 950, 600


class Renderer(object):

    def __init__(self):
        super(Renderer, self).__init__()

    def set_recompile_flag(self, should_recompile):
        self.should_recompile = should_recompile

    def uniform(self, u):
        if not self.program:
            return

        for n, v in u.items():
            if n in self.program:
                self.program[n].value = v

    def recompile(self, gl):
        def read(path):
            with open(path, 'r') as fp:
                return fp.read()

        self.should_recompile = False
        try:
            self.program = gl.program(
                vertex_shader=read("./gl/default_vs.glsl"),
                fragment_shader=read("./gl/default_fs.glsl"),
            )

            self.uniform({"u_resolution": (WIDTH, HEIGHT)})
            self.vao = gl.vertex_array(self.program, [(self.vbo, "2f", "in_pos")], self.ibo)

        except Exception as e:
            print(e)

    def init(self):
        self.gl = mg.create_context()
        gl = self.gl
        self.vbo = gl.buffer(
            np.array([-1.0, -1.0, -1.0, +1.0, +1.0, -1.0, +1.0, +1.0])
            .astype(np.float32)
            .tobytes()
        )
        self.ibo = gl.buffer(np.array([0, 1, 2, 2, 1, 3]).astype(np.int32).tobytes())

        self.recompile(gl)

        self.should_recompile = False
        handler = FileSystemEventHandler()
        handler.on_modified = lambda e: self.set_recompile_flag(True)
        watcher = Observer()
        watcher.schedule(handler, "./gl")
        watcher.start()

    def render(self):
        self.vao.render()

    def main(self):
        glfw.init()

        window = glfw.create_window(WIDTH, HEIGHT, "GLFW", None, None)
        glfw.make_context_current(window)

        self.init()

        t = glfw.get_time()
        while not glfw.window_should_close(window):

            if self.should_recompile:
                self.recompile(self.gl)

            self.render()

            glfw.swap_buffers(window)
            glfw.poll_events()

            elapsed_time = glfw.get_time() - t
            t = glfw.get_time()

            self.uniform({"u_time": t})

            FPS = 1.0 / elapsed_time
            FPS


if __name__ == "__main__":
    Renderer().main()
