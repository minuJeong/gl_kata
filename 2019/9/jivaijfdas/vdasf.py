import glfw
import moderngl as mg

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Renderer(object):
    def read(self, path):
        with open(path, 'r') as fp:
            return fp.read()

    def uniform(self, data):
        for p in self.programs:
            for n, v in data.items():
                if n in p:
                    p[n].value = v

    def __init__(self, width, height):
        super(Renderer, self).__init__()

        self.u_width, self.u_height = width, height

        self.programs = []

        self.gl = mg.create_context()
        self.vbo = self.gl.buffer(reserve=4 * 4 * 4)
        self.ibo = self.gl.buffer(reserve=6 * 4)
        self.vbo.bind_to_storage_buffer(0)
        self.ibo.bind_to_storage_buffer(1)

        self.recompile()

        def on_mod(e):
            self.should_recompile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_mod
        observer = Observer()
        observer.schedule(handler, "./gl/")
        observer.start()

    def recompile(self):
        self.should_recompile = False
        try:
            self.programs = []

            self.cs = self.gl.compute_shader(self.read("./gl/screen.glsl"))

            program = self.gl.program(
                vertex_shader=self.read("./gl/vertex.glsl"),
                fragment_shader=self.read("./gl/fragment.glsl"),
            )
            self.vao = self.gl.vertex_array(program, [(self.vbo, "4f", "in_pos")], self.ibo)

            self.programs.append(self.cs)
            self.programs.append(program)

            self.uniform({"u_width": self.u_width, "u_height": self.u_height})

            print("shaders recompiled")

        except Exception:
            print("---error---")

    def render(self, t):
        if self.should_recompile:
            self.recompile()

        self.uniform({"u_time": t})
        self.cs.run(1)
        self.vao.render()


def main():
    glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)

    width, height = 600, 400
    title = "good morning"
    window = glfw.create_window(width, height, title, None, None)
    glfw.make_context_current(window)
    renderer = Renderer(width, height)

    while not glfw.window_should_close(window):
        renderer.render(glfw.get_time())

        glfw.swap_buffers(window)
        glfw.poll_events()


if __name__ == "__main__":
    main()
