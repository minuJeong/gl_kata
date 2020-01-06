import glfw
import moderngl as mg
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def readbuffer(path):
    with open(path, "rb") as fp:
        return fp.read()


def readshader(path):
    with open(path, "r") as fp:
        return fp.read()


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()

        self.window = window
        self.gl = mg.create_context()

        self.compile()

        def on_modified(e):
            self.should_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_modified

        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

    def compile(self):
        self.should_compile = False

        try:
            self.N_PARTICLES = 1000 * 1000

            self.cs_initparticles = self.gl.compute_shader(readshader("./gl/initparticles.compute"))
            self.cs_updateparticles = self.gl.compute_shader(readshader("./gl/updateparticles.compute"))
            self.cs_populatequad = self.gl.compute_shader(readshader("./gl/populatequads.compute"))

            program = self.gl.program(
                vertex_shader=readshader("./gl/quad.vs"),
                fragment_shader=readshader("./gl/quad.fs"),
            )
            vb = self.gl.buffer(reserve=self.N_PARTICLES * 4 * 8 * 4)
            content = [(vb, "2f", "in_pos")]
            ib = self.gl.buffer(reserve=self.N_PARTICLES * 6 * 4)
            self.vao = self.gl.vertex_array(program, content, ib)

            self.cs_initparticles.run(self.N_PARTICLES // 64)

            vb.bind_to_storage_buffer(1)
            ib.bind_to_storage_buffer(2)

            print("compiled")

        except Exception as e:
            print(e)

    def uniform(self, program, uname, uvalue):
        if uname not in program:
            return

        if isinstance(uvalue, (float, int, bool)):
            program[uname].value = uvalue

        else:
            program[uname].write(bytes(uvalue))

    def update(self):
        if self.should_compile:
            self.compile()

        self.cs_updateparticles.run(self.N_PARTICLES // 64)

        self.uniform(self.vao.program, "u_time", glfw.get_time())
        self.vao.render()


def main():
    width, height = 1920, 1280

    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(width, height, "", None, None)
    glfw.make_context_current(window)

    client = Client(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        client.update()
        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
