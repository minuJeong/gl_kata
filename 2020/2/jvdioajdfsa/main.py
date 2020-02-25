import struct
from functools import reduce
from itertools import chain
from operator import add
from collections import OrderedDict

import moderngl as mg
import glfw
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Constant(object):
    glm_types = chain(
        (vec2, vec3, vec4),
        (ivec2, ivec3, ivec4),
        (uvec2, uvec3, uvec4),
        (mat2, mat3, mat4),
    )

    def __init__(self, gl, bind):
        super(Constant, self).__init__()

        self.gl = gl
        self.bind = bind

        self.data = OrderedDict()
        self.set("u_aspect", 1.0)
        self.set("u_time", 0.0)

    def get_size_value(self, value):
        if isinstance(value, (int, float, bool)):
            return 4
        elif isinstance(value, (vec2, ivec2, uvec2)):
            return 8
        elif isinstance(value, (vec3, ivec3, uvec3)):
            return 12
        elif isinstance(value, (vec4, ivec4, uvec4)):
            return 16
        elif isinstance(value, (mat2, imat2, umat2)):
            return 16

    def serialize_value(self, value):
        if isinstance(value, int):
            return struct.pack("1i", value)
        elif isinstance(value, float):
            return struct.pack("1f", value)
        elif isinstance(value, bool):
            return struct.pack("1?", value)
        elif isinstance(value, Constant.glm_types):
            return bytes(value)

    def set(self, uname, uvalue):
        # extend buffer if uname not registered already
        if uname not in self.data:
            new_size = self.get_size_value(uvalue)
            old_data = self.serialize_data()
            self.buffer = self.gl.buffer(reserve=self.get_size() + new_size)
            self.buffer.bind_to_storage_buffer(self.bind)
            if old_data:
                self.buffer.write(old_data)

        offset = self.get_offset(uname)
        self.buffer.write(self.serialize_value(uvalue), offset=offset)
        self.data[uname] = uvalue

    def get_offset(self, uname):
        cursor = 0
        for key, value in self.data.items():
            if key == uname:
                return cursor

            cursor += self.get_size_value(value)
        return cursor

    def get_size(self):
        return sum(map(self.get_size_value, self.data.values()))

    def serialize_data(self):
        values = []
        for value in self.data.values():
            values.append(self.serialize_value(value))

        if values:
            return reduce(add, values)
        else:
            return []

    def bind_buffer(self, size=0):
        if size:
            self.buffer = self.gl.buffer(reserve=size)
        else:
            data = self.serialize_data()
            self.buffer = self.gl.buffer(data)
        self.buffer.bind_to_storage_buffer(self.bind)


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()

        self.window = window

        self.gl = mg.create_context()
        self.compile_shaders()

        def onmod(e):
            self._should_compile = True

        h = FileSystemEventHandler()
        h.on_modified = onmod
        o = Observer()
        o.schedule(h, "./gl/", True)
        o.start()

        self.is_drag_window = False
        self.is_scale_window = False
        self.prev_pos = ivec2(0, 0)

        glfw.set_window_size_callback(window, self.on_window_size)
        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)

    def on_window_size(self, window, width, height):
        self.gl.viewport = (0, 0, width, height)
        self.uniform("u_aspect", float(width) / float(height))

    def on_mouse_button(self, window, button, action, mods):
        if action == glfw.PRESS:
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
            glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE)
            self.prev_pos = glfw.get_cursor_pos(window)

            if button == glfw.MOUSE_BUTTON_MIDDLE:
                self.is_drag_window = True
            elif button == glfw.MOUSE_BUTTON_RIGHT:
                self.is_scale_window = True
        elif action == glfw.RELEASE:
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.FALSE)
            if button == glfw.MOUSE_BUTTON_MIDDLE:
                self.is_drag_window = False
            elif button == glfw.MOUSE_BUTTON_RIGHT:
                self.is_scale_window = False

    def on_cursor_pos(self, window, x, y):
        pos = ivec2(x, y)
        delta = pos - self.prev_pos
        self.prev_pos = pos

        if self.is_drag_window:
            win_pos = ivec2(*glfw.get_window_pos(window))
            win_pos += delta
            glfw.set_window_pos(window, *win_pos)
        if self.is_scale_window:
            win_size = ivec2(*glfw.get_window_size(window))
            win_size += delta
            glfw.set_window_size(window, *win_size)

    def compile_shaders(self):
        self._should_compile = False
        self.scene = []

        try:
            VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)

            vertex_buffer = self.gl.buffer(reserve=4 * 4 * 4)
            vertex_buffer.bind_to_storage_buffer(0)
            content = [(vertex_buffer, "4f", "in_pos")]
            index_buffer = self.gl.buffer(reserve=6 * 4)
            index_buffer.bind_to_storage_buffer(1)

            self.const = Constant(self.gl, 2)

            cs_build_mesh = self.gl.compute_shader(open("./gl/build_mesh.glsl").read())
            cs_build_mesh.run(1)

            self.cs_update_mesh = self.gl.compute_shader(open("./gl/update_mesh.glsl").read())

            self.scene.append(self.gl.vertex_array(program, content, index_buffer))

            width, height = glfw.get_window_size(self.window)
            self.uniform("u_aspect", float(width) / float(height))

            print("shaders compiled.")

        except Exception as e:
            print(e)

    def uniform(self, uname, uvalue):
        self.const.set(uname, uvalue)

    def update(self):
        if self._should_compile:
            self.compile_shaders()

        self.gl.clear()
        self.uniform("u_time", glfw.get_time())
        self.cs_update_mesh.run()
        for node in self.scene:
            node.render()


def main():
    width, height = 800, 800

    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    window = glfw.create_window(width, height, "", None, None)
    glfw.make_context_current(window)
    monitor = glfw.get_primary_monitor()
    _, _, w, h = glfw.get_monitor_workarea(monitor)
    glfw.set_window_pos(window, w - width, h - height)

    client = Client(window)
    while not glfw.window_should_close(window):
        client.update()
        glfw.poll_events()
        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
