import moderngl as mg
import glfw

_any = any
from glm import *


ZERO = vec3(0.0)
UP = vec3(0.0, 1.0, 0.0)


def readbytes(path):
    with open(path, "rb") as fp:
        return fp.read()


class Render(object):
    def __init__(self, window, width, height):
        super(Render, self).__init__()
        self.window = window
        self.width, self.height = width, height

        self.gl = mg.create_context()

        data = readbytes("model_file.bin.gz")
        len_data = len(data)
        print(len_data)

        x = 34
        self.vbo = self.gl.buffer(data[:x])
        self.ibo = self.gl.buffer(data[x:])

        self.compile()

    def read_shader(self, path):
        with open(path, "r") as fp:
            return fp.read()

    def compile(self):
        try:
            self.program = self.gl.program(
                vertex_shader=self.read_shader("./gl/vs_a.glsl"),
                fragment_shader=self.read_shader("./gl/fs_a.glsl"),
            )
            self.vao = self.gl.vertex_array(
                self.program, [(self.vbo, "4f", "in_pos")], self.ibo, skip_errors=True
            )

        except Exception as e:
            print("failed to compile shaders..")
            print(e)

    def uniform(self, n, v):
        bintypes = (mat4, vec2, vec3, vec4)
        if n in self.program:
            if isinstance(v, bintypes):
                self.program[n].write(bytes(v))
            else:
                self.program[n].value = v

    def render(self):
        # T = glfw.get_time()

        u_MV = mat4(
            0.5810,
            -0.1779,
            0.7942,
            0,
            0.8139,
            0.1270,
            -0.5670,
            0,
            0,
            0.9758,
            0.2185,
            0,
            0.0674,
            -2.4369,
            -709.4822,
            1,
        )
        u_P = mat4(
            64.1323,
            0,
            0,
            0,
            0,
            114.5887,
            0,
            0,
            0,
            0,
            -11.8994,
            -1,
            0,
            0,
            -8395.1123,
            0.0,
        )

        self.uniform("uQVT", vec3(-33.3857, -33.3857, -0.9568))
        self.uniform("uQVS", vec3(6.9499, 10.2903, 0.9103))
        self.uniform("uDisplay2D", 0.0)
        self.uniform("uGlobalTexRatio", vec2(1.0, 1.0))
        self.uniform("uGlobalTexSize", vec2(1349, 755))
        self.uniform("uHalton", vec4(-0.0140, 0.0344, 1.0, 3.0))
        self.uniform("uProjectionMatrix", u_P)
        self.uniform("uModelViewMatrix", u_MV)

        self.gl.clear()
        self.vao.render()


def main():

    glfw.init()
    width, height = 512, 512
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(width, height, "hi", None, None)
    glfw.make_context_current(window)

    r = Render(window, width, height)

    while not glfw.window_should_close(window):
        r.render()
        glfw.swap_buffers(window)
        glfw.poll_events()


if __name__ == "__main__":
    main()
