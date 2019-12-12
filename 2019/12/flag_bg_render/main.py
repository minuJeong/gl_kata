import struct
from collections import OrderedDict

import numpy as np
import moderngl as mg
import imageio as iio
import glfw
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ConstBuffer(object):
    structpack_mapping = {
        float: "1f",
        int: "1i",
    }

    glmtypes = (
        vec2,
        vec3,
        vec4,
        ivec2,
        ivec3,
        ivec4,
        uvec2,
        uvec3,
        uvec4,
        mat2,
        mat3,
        mat4,
    )

    def __init__(self, gl):
        super(ConstBuffer, self).__init__()
        self.gl = gl
        self._data = OrderedDict({"u_time": 0.0})
        self.bind_index = -1
        self._reconstruct_buffer()

    def _reconstruct_buffer(self):
        self.gl_buffer = self.gl.buffer(self.bytespack())
        if self.bind_index > 0:
            self.gl_buffer.bind_to_storage_buffer(self.bind_index)

    def _len_value(self, value):
        if isinstance(value, (float, int)):
            return 4
        else:
            return sizeof(value)

    def _bytes_value(self, value):
        if type(value) in ConstBuffer.structpack_mapping:
            return struct.pack(ConstBuffer.structpack_mapping[type(value)], value)
        elif isinstance(value, ConstBuffer.glmtypes):
            return bytes(value)

    def set_data(self, target_key, target_value):
        cursor = 0
        for k, v in self._data.items():
            if k == target_key:
                self._data[k] = target_value
                self.gl_buffer.write(self._bytes_value(target_value), offset=cursor)
                return
            else:
                cursor += self._len_value(v)

        # key not found: expand _data and reconstruct buffer
        self._data[target_key] = target_value
        self._reconstruct_buffer()

    def len_bytes(self):
        size = 0
        for v in self._data.values():
            size += self._len_value(v)
        return size

    def bytespack(self):
        packed_bytes = bytes()
        for v in self._data.values():
            packed_bytes += self._bytes_value(v)
        return packed_bytes

    def bind_to_storage_buffer(self, i):
        self.bind_index = i
        self.gl_buffer.bind_to_storage_buffer(self.bind_index)


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()

        self.width, self.height = glfw.get_window_size(window)
        self.init_gl()

        h = FileSystemEventHandler()
        h.on_modified = self.on_modified
        o = Observer()
        o.schedule(h, "./gl", True)
        o.start()

        self.is_drag_window = False
        self.precursor = ivec2(0.0, 0.0)
        self.is_recording = False

        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)
        glfw.set_key_callback(window, self.on_key)

    def on_modified(self, e):
        self._should_compile = True

    def on_mouse_button(self, window, button, action, mods):
        if action == glfw.PRESS:
            glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE)
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

            if button == glfw.MOUSE_BUTTON_MIDDLE:
                self.is_drag_window = True

        elif action == glfw.RELEASE:
            glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.FALSE)
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

            if button == glfw.MOUSE_BUTTON_MIDDLE:
                self.is_drag_window = False

    def on_cursor_pos(self, window, x, y):
        dx, dy = self.precursor.x - x, self.precursor.y - y

        if self.is_drag_window:
            wx, wy = glfw.get_window_pos(window)
            wx, wy = wx - dx, wy - dy
            glfw.set_window_pos(window, int(wx), int(wy))

        self.precursor.x, self.precursor.y = x, y

    def on_key(self, window, scancode, keycode, action, mods):
        if action == glfw.RELEASE:
            if scancode == glfw.KEY_SPACE:
                if self.is_recording:
                    self.writer.close()
                    self.is_recording = False
                else:
                    self.writer = iio.get_writer("record.mp4", fps=60)
                    self.is_recording = True

    def read(self, path):
        with open(path, "r") as fp:
            return fp.read()

    def init_gl(self):
        self.gl = mg.create_context()
        self.const = ConstBuffer(self.gl)
        self.const.bind_to_storage_buffer(5)
        self.const.set_data("u_aspect", self.width / self.height)

        vb = []
        for x in range(-1, 2, 2):
            for y in range(-1, 2, 2):
                vb.extend([x, y, 0, 1.0])

        self.vbo = self.gl.buffer(struct.pack("16f", *vb))
        self.vbcontent = [(self.vbo, "4f", "in_pos")]
        self.ibo = self.gl.buffer(struct.pack("6i", 0, 1, 2, 2, 1, 3))
        self.compile()

    def compile(self):
        self._should_compile = False

        try:
            VS, FS = self.read("./gl/vs.glsl"), self.read("./gl/fs.glsl")
            self.program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            self.vertex_array = self.gl.vertex_array(
                self.program, self.vbcontent, self.ibo, skip_errors=True
            )
            print("compiled")

        except Exception as e:
            print(e)

    def paint_gl(self):
        self.vertex_array.render()

    def record_frame(self):
        framedata = self.gl.screen.read(components=3)
        framedata = np.frombuffer(framedata, dtype=np.ubyte).reshape((self.height, self.width, 3))
        self.writer.append_data(framedata)

    def update(self):
        if self._should_compile:
            self.compile()

        self.const.set_data("u_time", glfw.get_time())
        self.gl.clear()
        self.paint_gl()

        if self.is_recording:
            self.record_frame()

    def close(self):
        if self.is_recording:
            self.writer.close()


def main():
    width, height = 1920, 1088
    title = "hello"

    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(width, height, title, None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        client.update()
        glfw.swap_buffers(window)

    client.close()


if __name__ == "__main__":
    main()
