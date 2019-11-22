import moderngl as mg
import numpy as np
import glfw
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


UP = vec3(0.0, 1.0, 0.0)


def _readshaderfile(path):
    with open(path, "r") as fp:
        content = fp.read()

    inc = "#include "

    parsed_lines = []
    for line in content.splitlines():
        if line.startswith(inc):
            path = line.split(inc)[1]
            parsed_lines.append(_readshaderfile(path))
            continue

        parsed_lines.append(line)

    return "\n".join(parsed_lines)


class Actor(object):
    def uniform(self, p, n, v):
        if n not in p:
            return

        if isinstance(v, (vec2, vec3, vec4, mat4)):
            p[n].write(bytes(v))

        else:
            p[n].value = v


class Cube(Actor):
    def __init__(self):
        super(Cube, self).__init__()

    def init_gl(self, gl):
        self.gl = gl

        self.compile()

        self.u_M = mat4(1.0)

    def compile(self):
        try:
            cs_source_build_cube = _readshaderfile("./gl/cs/build_cube.glsl")
            cs_source_compute_normal = _readshaderfile("./gl/cs/compute_normal.glsl")

            vs_source = _readshaderfile("./gl/vs_cube.glsl")
            fs_source = _readshaderfile("./gl/fs_cube.glsl")

            self.vbo = self.gl.buffer(reserve=(4 + 4 + 4) * 8 * (4))
            self.ibo = self.gl.buffer(
                np.array(
                    (
                        ((0, 2, 1), (3, 1, 2)),
                        ((0, 4, 6), (0, 6, 2)),
                        ((5, 7, 4), (7, 6, 4)),
                        ((5, 1, 3), (5, 3, 7)),
                        ((4, 0, 5), (5, 0, 1)),
                        ((2, 6, 3), (6, 7, 3)),
                    )
                )
                .astype(np.int32)
                .tobytes()
            )

            self.vbo.bind_to_storage_buffer(0)
            self.ibo.bind_to_storage_buffer(1)

            self.cs_build_cube = self.gl.compute_shader(cs_source_build_cube)
            self.cs_compute_normal = self.gl.compute_shader(cs_source_compute_normal)

            self.program = self.gl.program(
                vertex_shader=vs_source, fragment_shader=fs_source
            )

            self.vao = self.gl.vertex_array(
                self.program,
                [(self.vbo, "4f 4f 4f", "in_position", "in_normal", "in_texcoord0")],
                self.ibo,
                skip_errors=True,
            )
            print(f"[Cube] shaders compiled at: {glfw.get_time()}")

        except Exception as e:
            print("[Cube] shader compile error: ", e)

    def render(self, u_V=None, u_P=None):
        u_V = u_V or mat4(1.0)
        u_P = u_P or mat4(1.0)

        u_MVP = u_P * u_V * self.u_M
        self.uniform(self.program, "u_MVP", u_MVP)
        self.uniform(self.cs_build_cube, "u_time", glfw.get_time())

        try:
            self.cs_build_cube.run(1)
            self.cs_compute_normal.run(1)

            self.vao.render()

            self.gl.point_size = 10.0
            self.vao.render(mg.POINTS)

        except Exception as e:
            print(e)


class Scene(object):
    def __init__(self, window, width, height):
        super(Scene, self).__init__()

        self.window = window
        self.width, self.height = width, height
        self.aspect = self.width / self.height

        self.gl = mg.create_context()

        self.init()

    def on_gl_modified(self, e):
        self.should_compile = True

    def init(self):
        self.init_scene()
        self.init_camera()
        self.init_observer()

        self.compile()

    def init_observer(self):
        handler = FileSystemEventHandler()
        handler.on_modified = self.on_gl_modified
        observer = Observer()
        observer.schedule(handler, "./gl/", True)
        observer.start()

    def init_scene(self):
        self.nodes = []

        cube = Cube()
        cube.init_gl(self.gl)
        self.nodes.append(cube)

    def init_camera(self):
        self.cam_pos = vec3(-5.0, 5.0, -5.0)
        self.cam_look = vec3(0.0, 0.0, 0.0)
        self.u_V = lookAt(self.cam_pos, self.cam_look, UP)
        self.u_P = perspective(radians(74.0), self.aspect, 0.02, 100.0)

    def compile(self):
        self.should_compile = False
        for node in self.nodes:
            node.compile()

    def update_camera(self):
        self.u_V = rotate(self.u_V, 0.14, UP)

    def render(self):
        if self.should_compile:
            self.compile()

        self.update_camera()

        self.gl.clear()
        self.gl.enable(mg.CULL_FACE)
        self.gl.enable(mg.DEPTH_TEST)
        for node in self.nodes:
            node.render(self.u_V, self.u_P)


def main():
    glfw.init()

    width, height = 1200, 800

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(width, height, "hello", None, None)
    glfw.make_context_current(window)

    render = Scene(window, width, height)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        render.render()

        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
