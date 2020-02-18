import struct

from glm import *
import moderngl as mg
import numpy as np
import glfw
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Client(object):
    CONST_BUFFER = {"u_time": 0}

    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window

        self.is_drag = False
        self.offset = ivec2(0, 0)
        self.prevpos = ivec2(0, 0)

        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)

        self.gl = mg.create_context()
        assert self.gl

        self.compile()

        def onmod(e):
            self.need_compile = True

        h = FileSystemEventHandler()
        h.on_modified = onmod
        o = Observer()
        o.schedule(h, "./gl/", True)
        o.start()

    def on_mouse_button(self, window, button, action, mods):
        if action == glfw.PRESS:
            self.is_drag = True
            self.offset = ivec2(*glfw.get_cursor_pos(window))
            self.prevpos = ivec2(*glfw.get_window_pos(window))
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
            glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE)
        elif action == glfw.RELEASE:
            self.is_drag = False
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.FALSE)

    def on_cursor_pos(self, window, x, y):
        if self.is_drag:
            xy = ivec2(*glfw.get_cursor_pos(window)) + self.prevpos - self.offset
            glfw.set_window_pos(window, xy.x, xy.y)

    def compile(self):
        self.need_compile = False
        try:
            VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            vertices = np.array([-1, -1, -1, 1, 1, -1, 1, 1], dtype=np.float32)
            indices = np.array([0, 1, 2, 2, 1, 3], dtype=np.int32)
            vbo = self.gl.buffer(vertices)
            ibo = self.gl.buffer(indices)
            self.screen_quad = self.gl.vertex_array(
                program, [(vbo, "2f", "in_pos")], ibo
            )

            self.constbuffer = self.gl.buffer(reserve=4)
            self.constbuffer.bind_to_storage_buffer(0)
            print("compiled")

        except Exception as e:
            print(e)

    def uniform(self, uoffset, uvalue):
        self.constbuffer.write(uvalue, offset=uoffset)

    def update(self):
        if self.need_compile:
            self.compile()

        self.uniform(Client.CONST_BUFFER["u_time"], struct.pack("f", glfw.get_time()))
        self.screen_quad.render()


def main():
    WIDTH, HEIGHT = 400, 400
    glfw.init()
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, "", None, None)
    monitor = glfw.get_primary_monitor()
    x, y, w, h = glfw.get_monitor_workarea(monitor)
    glfw.set_window_pos(window, (w >> 1) - (WIDTH >> 1), (h >> 1) - (HEIGHT >> 1))
    glfw.make_context_current(window)
    client = Client(window)
    while not glfw.window_should_close(window):
        glfw.swap_buffers(window)
        glfw.poll_events()
        client.update()


if __name__ == "__main__":
    main()
