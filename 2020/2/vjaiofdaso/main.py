import glfw
import numpy as np
import moderngl as mg
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from const import WIDTH, HEIGHT, WINDOW_TITLE


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window

        self.prev_cursor = ivec2(0.0, 0.0)
        self.is_drag_win = False

        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)

        self.gl = mg.create_context()
        self._compile()

        def set_need_compile():
            self._need_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = lambda e: set_need_compile()
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

    def on_mouse_button(self, window, button, action, mods):
        if action == glfw.PRESS:
            if button == glfw.MOUSE_BUTTON_MIDDLE:
                self.is_drag_win = True
                self.prev_cursor = ivec2(glfw.get_cursor_pos(window))
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE)
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        elif action == glfw.RELEASE:
            if button == glfw.MOUSE_BUTTON_MIDDLE:
                self.is_drag_win = False
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.FALSE)
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def on_cursor_pos(self, window, x, y):
        pos = ivec2(x, y)
        delta = pos - self.prev_cursor
        self.prev_cursor = pos
        if self.is_drag_win:
            new_pos = ivec2(glfw.get_window_pos(window)) + delta
            glfw.set_window_pos(window, *new_pos)

    def _compile(self):
        self._need_compile = False

        try:
            self.scene = []

            VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
            self.program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            p, q = vec4(-1.0, -1.0, 0.0, 1.0), vec4(-1.0, +1.0, 0.0, 1.0)
            r, t = vec4(+1.0, -1.0, 0.0, 1.0), vec4(+1.0, +1.0, 0.0, 1.0)
            vertices = self.gl.buffer(np.array((*p, *q, *r, *t), dtype=np.float32))
            indices = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))
            self.scene.append(
                self.gl.vertex_array(
                    self.program, [(vertices, "4f", "in_pos")], indices
                )
            )

            print("compiled")

        except Exception as e:
            print(e)

    def uniform(self, uname, uvalue):
        if uname in self.program:
            self.program[uname] = uvalue

    def update(self):
        if self._need_compile:
            self._compile()

        self.uniform("u_time", glfw.get_time())

        for node in self.scene:
            node.render()


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, WINDOW_TITLE, None, None)
    glfw.make_context_current(window)
    client = Client(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
