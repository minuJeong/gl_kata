import moderngl as mg
import numpy as np
import glfw

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Renderer(object):
    def read(self, path):
        with open(path, "r") as fp:
            context = fp.read()

        lines = []
        for line in context.splitlines():
            if line.startswith("#include "):
                lines.append(self.read(line.split("#include ")[1]))
            else:
                lines.append(line)

        return "\n".join(lines)

    def init(self):
        self.gl = mg.create_context()
        self.vbo = [
            (
                self.gl.buffer(
                    np.array([-1.0, -1.0, -1.0, +1.0, +1.0, -1.0, +1.0, +1.0])
                    .astype(np.float32)
                    .tobytes()
                ),
                "2f",
                "in_pos",
            )
        ]
        self.ibo = self.gl.buffer(
            np.array([0, 1, 2, 2, 1, 3]).astype(np.int32).tobytes()
        )

        self.recompile()

        self.should_recompile = False

        def set_recompile_flag():
            self.should_recompile = True

        handler = FileSystemEventHandler()
        handler.on_modified = lambda e: set_recompile_flag()
        observer = Observer()
        observer.schedule(handler, "./gl")
        observer.start()

    def recompile(self):
        self.should_recompile = False

        try:
            self.program = self.gl.program(
                vertex_shader=self.read("./gl/vertex_shader.glsl"),
                fragment_shader=self.read("./gl/fragment_shader.glsl"),
            )

            self.vao = self.gl.vertex_array(self.program, self.vbo, self.ibo)
            print("recompiled")

        except Exception as e:
            print(e)

    def uniform(self, uniform_data):
        for n, v in uniform_data.items():
            if n in self.program:
                self.program[n].value = v

    def render(self):
        self.uniform({"u_time": glfw.get_time()})
        self.vao.render()

    def start(self):
        glfw.init()
        glfw.window_hint(glfw.FLOATING, glfw.TRUE)
        self.window = glfw.create_window(700, 700, "GLFW Preview", None, None)
        glfw.make_context_current(self.window)

        self.init()

        while not glfw.window_should_close(self.window):

            if self.should_recompile:
                self.recompile()

            self.render()

            glfw.swap_buffers(self.window)
            glfw.poll_events()


def main():
    renderer = Renderer()
    renderer.start()


if __name__ == "__main__":
    main()
