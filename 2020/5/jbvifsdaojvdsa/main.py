import struct
from functools import reduce

import glfw
import moderngl as mg
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from const import WIDTH, HEIGHT


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window

        self.init_window()
        self.init_gl()
        self.init_watchdog()

    def init_window(self):
        window_width, window_height = glfw.get_window_size(self.window)
        _, _, center_x, center_y = glfw.get_monitor_workarea(glfw.get_primary_monitor())
        window_x = (center_x // 2) - (window_width // 2)
        window_y = (center_y // 2) - (window_height // 2)
        glfw.set_window_pos(self.window, window_x, window_y)

    def init_gl(self):
        self.gl_context = mg.create_context()
        self.compile_shaders()

    def init_watchdog(self):
        def on_modified(e):
            self.should_reload_shaders = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_modified
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

    def build_grid_points(self):
        size = 0.2
        count = 0
        vertices = []
        for z in range(-5, 5):
            for x in range(-5, 5):
                vertices.extend([*vec4(x * size, 0.0, z * size, 1.0)])
                count += 1

        return struct.pack(f"{count * 4}f", *vertices)

    def compile_shaders(self):
        self.should_reload_shaders = False
        try:
            vertex_shader_source = open("./gl/quad.vs").read()
            geometry_shader_source = open("./gl/quad.gs").read()
            fragment_shader_source = open("./gl/quad.fs").read()
            program = self.gl_context.program(
                vertex_shader=vertex_shader_source,
                geometry_shader=geometry_shader_source,
                fragment_shader=fragment_shader_source,
            )
            vertices_buffer = self.gl_context.buffer(self.build_grid_points())
            vertex_content = [(vertices_buffer, "4f", "in_pos")]
            self.quad = self.gl_context.vertex_array(program, vertex_content)

            self.camera_pos = vec3(-0.7, 1.4, -1.5)
            self.uniform("u_camera_pos", self.camera_pos)

            view = lookAt(self.camera_pos, vec3(0.0), vec3(0.0, 1.0, 0.0))
            proj = perspective(radians(94.0), 1.0, 0.1, 1000.0)
            self.uniform("u_mvp", proj * view)
            print("shaders compiled")

        except Exception as e:
            print(e)

    def uniform(self, uniform_name, uniform_value):
        assert self.quad is not None
        assert isinstance(uniform_name, str)
        assert uniform_value is not None

        program = self.quad.program
        if uniform_name not in program:
            return

        if isinstance(uniform_value, (float, int, bool)):
            program[uniform_name] = uniform_value
        elif isinstance(
            uniform_value, (vec2, vec3, vec4, ivec2, ivec3, ivec4, uvec2, uvec3, uvec4)
        ):
            program[uniform_name] = (*uniform_value,)
        elif isinstance(uniform_value, (mat2, mat3, mat4)):
            serialized = tuple([value for row in uniform_value for value in row])
            program[uniform_name] = serialized
        else:
            raise Exception(f"unhandled uniform type: {uniform_value}")

    def update(self):
        if self.should_reload_shaders:
            self.compile_shaders()

        self.uniform("u_time", glfw.get_time())

        self.gl_context.clear()
        self.gl_context.enable(mg.CULL_FACE)
        self.gl_context.enable(mg.DEPTH_TEST)
        self.quad.render(mode=mg.POINTS)


def main():
    assert glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, "", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.swap_buffers(window)
        glfw.poll_events()
        client.update()


if __name__ == "__main__":
    main()
