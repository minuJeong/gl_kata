import numpy as np
import moderngl as mg
import glfw
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from util import mat4_to_tuple
from const import ZERO, UP


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window

        self.isdrag_camera = False
        self.isdrag_window = False
        self.prev_cursor = vec2(0, 0)
        self.campos = vec3(-2.0, 3.0, -2.0)

        self.init()

        # set window center to the screen
        m = glfw.get_primary_monitor()
        ww, hh = glfw.get_window_size(window)
        x, y, w, h = glfw.get_monitor_workarea(m)
        glfw.set_window_pos(window, w // 2 - ww // 2, h // 2 - hh // 2)

        # mouse event
        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)
        glfw.set_scroll_callback(window, self.on_scroll)
        glfw.set_key_callback(window, self.on_key)

    def on_mouse_button(self, window, button, action, mods):
        if action == glfw.PRESS:
            glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE)
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
            if button == glfw.MOUSE_BUTTON_LEFT:
                self.isdrag_camera = True
            elif button == glfw.MOUSE_BUTTON_MIDDLE:
                self.isdrag_window = True

        elif action == glfw.RELEASE:
            glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.FALSE)
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            if button == glfw.MOUSE_BUTTON_LEFT:
                self.isdrag_camera = False
            elif button == glfw.MOUSE_BUTTON_MIDDLE:
                self.isdrag_window = False

    def on_cursor_pos(self, window, x, y):
        p = vec2(x, y)
        delta = self.prev_cursor - p
        self.prev_cursor = p

        if self.isdrag_camera:
            view = normalize(self.campos)
            right = cross(view, UP)
            campos4 = vec4(self.campos.xyz, 1.0)
            campos4 = (
                rotate(rotate(mat4(1.0), delta.x * 0.001, UP), delta.y * -0.001, right)
                * campos4
            )
            self.campos = campos4.xyz

        if self.isdrag_window:
            x, y = glfw.get_window_pos(window)
            x, y = int(x - delta.x), int(y - delta.y)
            glfw.set_window_pos(window, x, y)

    def on_scroll(self, window, x, y):
        cam_direction = normalize(self.campos)
        self.campos += y * cam_direction * 0.1

    def on_key(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE:
            if action == glfw.PRESS:
                glfw.set_window_should_close(window, glfw.TRUE)

    def init(self):
        self.gl = mg.create_context()
        self.compile()

        def set_need_compile():
            self._need_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = lambda e: set_need_compile()
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

    def compile(self):
        self._need_compile = False

        try:
            vertices = []
            indices = []

            forward = vec3(0.0, 0.0, 1.0) * 0.5
            right = vec3(1.0, 0.0, 0.0) * 0.5
            i = 0
            resolution = 5
            inv_resolution = 1.0 / resolution
            for x in range(-resolution, resolution):
                for z in range(-resolution, resolution):
                    p = vec3(x, 0.0, z) * inv_resolution
                    vertices.extend([*vec4(p + vec3(-right - forward) * inv_resolution, 1.0)])
                    vertices.extend([*vec4(p + vec3(+right - forward) * inv_resolution, 1.0)])
                    vertices.extend([*vec4(p + vec3(-right + forward) * inv_resolution, 1.0)])
                    vertices.extend([*vec4(p + vec3(+right + forward) * inv_resolution, 1.0)])
                    indices.extend([i + 0, i + 2, i + 1, i + 1, i + 2, i + 3])
                    i += 4

            vb = self.gl.buffer(np.array(vertices, dtype=np.float32))
            ib = self.gl.buffer(np.array(indices, dtype=np.int32))
            VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            self.vao = self.gl.vertex_array(program, [(vb, "4f", "in_pos")], ib)

            print("compiled")

        except Exception as e:
            print(e)

    def uniform(self, program, uname, uvalue):
        if uname in program:
            if isinstance(uvalue, mat4):
                uvalue = mat4_to_tuple(uvalue)
            program[uname] = uvalue

    def update(self):
        if self._need_compile:
            self.compile()
            return

        self.uniform(self.vao.program, "u_view", lookAt(self.campos, ZERO, UP))
        self.uniform(
            self.vao.program,
            "u_perspective",
            perspectiveFov(radians(74.0), 1280, 720, 0.01, 1000.0),
        )
        self.uniform(self.vao.program, "u_time", glfw.get_time())

        self.gl.clear()
        # self.gl.enable(mg.CULL_FACE)

        self.gl.wireframe = True
        self.vao.render()


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    window = glfw.create_window(1280, 720, "", None, None)
    glfw.make_context_current(window)
    client = Client(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
