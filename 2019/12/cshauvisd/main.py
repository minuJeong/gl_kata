import numpy as np
import moderngl as mg
import imageio as ii
import glfw
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def read(path):
    with open(path, "r") as fp:
        return fp.read()


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window
        self.width, self.height = glfw.get_window_size(window)

        self.gl = mg.create_context()
        self.compile()

        img = ii.imread("texture.tga")
        self.tex = self.gl.texture((img.shape[1], img.shape[0]), img.shape[2], img.tobytes())

        def on_modified(e):
            self.should_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_modified
        observer = Observer()
        observer.schedule(handler, "./gl/", True)
        observer.start()

    def compile(self):
        self.should_compile = False

        try:
            VS, FS = read("./gl/quad.vs"), read("./gl/quad.fs")
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            vb = np.array([-1, -1, -1, 1, 1, -1, 1, 1], dtype=np.float32)
            ib = np.array([0, 1, 2, 2, 1, 3], dtype=np.int32)
            vb, ib = self.gl.buffer(vb), self.gl.buffer(ib)
            self.vao = self.gl.vertex_array(program, [(vb, "2f", "in_pos")], ib, skip_errors=True)

            u_aspect = self.width / self.height
            self.uniform(program, "u_aspect", u_aspect)

            print("done")

        except Exception as e:
            print(e)

    def uniform(self, program, uname, uvalue):
        if uname not in program:
            return

        if isinstance(uvalue, (float, int)):
            program[uname].value = uvalue
        else:
            program[uname].write(bytes(uvalue))

    def update(self):
        if self.should_compile:
            self.compile()

        self.uniform(self.vao.program, "u_time", glfw.get_time())
        self.uniform(self.vao.program, "u_texture", 0)
        self.tex.use(0)
        self.vao.render()


def main():
    WIDTH, HEIGHT = 800, 600

    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, "hello, opengl", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
