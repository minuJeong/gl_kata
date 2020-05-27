import struct

import moderngl as mg
import glfw
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


WIDTH, HEIGHT = 800, 600
TITLE = "Hello World"


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window
        self.init()

    def init(self):
        # init gl
        self.gl = mg.create_context()
        self.compile_shaders()

        handler = FileSystemEventHandler()
        handler.on_modified = self.on_modified
        observer = Observer()
        observer.schedule(handler, "./gl/", True)
        observer.start()

    def on_modified(self, e):
        self.need_compile = True

    def compile_shaders(self):
        self.need_compile = False
        try:
            vs_src, fs_src = open("./gl/quad.vs").read(), open("./gl/quad.fs").read()
            program = self.gl.program(vertex_shader=vs_src, fragment_shader=fs_src)

            vertices = struct.pack(
                "16f",
                *(
                    *vec4(-1.0, -1.0, 0.0, 1.0),
                    *vec4(-1.0, +1.0, 0.0, 1.0),
                    *vec4(+1.0, -1.0, 0.0, 1.0),
                    *vec4(+1.0, +1.0, 0.0, 1.0),
                )
            )
            indices = struct.pack("6i", 0, 1, 2, 2, 1, 3)
            content = [(self.gl.buffer(vertices), "4f", "in_pos")]
            index_buffer = self.gl.buffer(indices)
            self.quad = self.gl.vertex_array(program, content, index_buffer)

            self.uniform("u_resolution", vec2(WIDTH, HEIGHT))

            print("compiled shaders")

        except Exception as e:
            print(e)

    def uniform(self, uname, uvalue):
        assert isinstance(uname, str)
        assert uvalue is not None
        assert self.quad is not None

        program = self.quad.program
        if uname not in program:
            return

        if isinstance(uvalue, (float, int, bool)):
            program[uname] = uvalue
        elif (
            isinstance(uvalue, (vec2, vec3, vec4))
            or isinstance(uvalue, (ivec2, ivec3, ivec4))
            or isinstance(uvalue, (uvec2, uvec3, uvec4))
        ):
            program[uname] = (*uvalue,)
        elif isinstance(uvalue, (mat2, mat3, mat4)):
            program[uname] = tuple([v for row in uvalue for v in row])

    def update(self):
        if self.need_compile:
            self.compile_shaders()

        self.uniform("u_time", glfw.get_time())
        self.quad.render()


def main():
    assert glfw.init(), "failed initializing glfw"

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, TITLE, None, None)
    if window is None:
        print("failed to create window")
        return
    glfw.make_context_current(window)

    client = Client(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
