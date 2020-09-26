import struct

import glfw
import moderngl as mg
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Shader(object):
    def __init__(self, gl, vertex_shader, geometry_shader=None, fragment_shader=None):
        super().__init__()
        self.gl = gl
        self.vertex_shader = open(vertex_shader).read()
        if geometry_shader:
            self.geometry_shader = open(geometry_shader).read()
        self.fragment_shader = open(fragment_shader).read()

    def compile(self):
        if hasattr(self, "geometry_shader"):
            self.program = self.gl.program(
                vertex_shader=self.vertex_shader,
                geometry_shader=self.geometry_shader,
                fragment_shader=self.fragment_shader,
            )

        else:
            self.program = self.gl.program(
                vertex_shader=self.vertex_shader, fragment_shader=self.fragment_shader
            )

    def uniform(self, uniform):
        assert self.program is not None
        for key, value in uniform.items():
            if key not in self.program:
                continue

            self.program[key] = value


class Material(object):
    def __init__(self, shader, uniform_data):
        super().__init__()
        self.shader = shader
        self.uniform_data = uniform_data

        assert self.shader
        assert self.uniform_data is not None

    def compile(self):
        self.shader.compile()
        self.shader.uniform(self.uniform_data)

    def uniform(self, uniform):
        self.shader.uniform(uniform)


class Mesh(object):
    gl = None
    material = None

    def __init__(self, gl, material=None):
        super().__init__()
        self.gl = gl

        if material is None:
            material = Material(
                Shader(self.gl, "./gl/quad.vs", None, "./gl/quad.fs"), {}
            )
        self.material = material
        assert self.material, "material should exists"

        if not hasattr(self.material.shader, "program"):
            self.material.compile()

        self.build()
        assert self.vertex_array, "self.vertex_array must be initialized in func build"

    def compile(self):
        self.material.compile()

    def build(self):
        """ override this """
        pass

    def render(self):
        """ override this """
        self.vertex_array.render()


class ScreenQuad(Mesh):
    def build(self):
        vertices = []
        for x in range(-1, 2, 2):
            for y in range(-1, 2, 2):
                vertices.extend([x, y, 0.0, 1.0])

        self.vertex_buffer = self.gl.buffer(struct.pack(f"{4 * 4}f", *vertices))
        indices = [0, 1, 2, 2, 1, 3]
        self.index_buffer = self.gl.buffer(struct.pack("6i", *indices))
        self.vertex_array = self.gl.vertex_array(
            self.material.shader.program,
            [(self.vertex_buffer, "4f", "in_pos")],
            self.index_buffer,
        )

    def render(self):
        self.vertex_array.render()


class Client(object):
    def __init__(self, window):
        super().__init__()

        self.window = window
        self.gl = mg.create_context()
        assert self.gl, "failed to create gl context"

        self.compile()

        def on_mod(e):
            self._need_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_mod
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

    def compile(self):
        self._need_compile = False

        try:
            shader = Shader(self.gl, "./gl/quad.vs", None, "./gl/quad.fs")
            self.material = Material(shader, {"u_resolution": (800, 600)})
            self.quad = ScreenQuad(self.gl, self.material)
            print("compiled")

        except Exception as e:
            print(e)

    def update(self):
        if self._need_compile:
            self.compile()
            return

        self.quad.material.uniform({"u_time", glfw.get_time()})
        self.quad.render()


def main():
    assert glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(800, 600, "", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
