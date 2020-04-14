import struct

import moderngl as mg
import glfw
from glm import *


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window

        self.init()

        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)

    def on_mouse_button(self, window, button, action, mods):
        pass

    def on_cursor_pos(self, window, x, y):
        pass

    def init(self):
        self.gl = mg.create_context()
        self._compile()

    def _compile(self):
        try:
            VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
            p = self.gl.program(vertex_shader=VS, fragment_shader=FS)

            vertices = (
                *(*vec4(-1.0, -1.0, 0.0, 1.0), *vec4(+1.0, -1.0, 0.0, 1.0)),
                *(*vec4(-1.0, +1.0, 0.0, 1.0), *vec4(+1.0, +1.0, 0.0, 1.0)),
            )
            vb = self.gl.buffer(struct.pack("16f", *vertices))
            ib = self.gl.buffer(struct.pack("6i", 0, 1, 2, 2, 1, 3))
            self.vao = self.gl.vertex_array(p, [(vb, "4f", "in_pos")], ib)

        except Exception as e:
            print(e)

    def update(self):
        self.vao.render()


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
    w = glfw.create_window(600, 600, "texture", None, None)
    glfw.make_context_current(w)
    c = Client(w)

    while not glfw.window_should_close(w):
        glfw.poll_events()
        glfw.swap_buffers(w)
        c.update()


if __name__ == "__main__":
    main()
