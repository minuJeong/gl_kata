import struct

import glfw
from glm import *
import moderngl as mg


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()

        self.window = window

        m = glfw.get_primary_monitor()
        _, _, w, h = glfw.get_monitor_workarea(m)
        ww, hh = glfw.get_window_size(window)
        glfw.set_window_pos(window, w // 2 - ww // 2, h // 2 - hh // 2)

        self._isdrag = False
        self._prevpos = ivec2(0, 0)

        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)

    # public
    def init(self):
        self.gl = mg.create_context()

        self._compile()

    def on_mouse_button(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_MIDDLE:
            if action == glfw.PRESS:
                self._isdrag = True
                self._prevpos = ivec2(*glfw.get_cursor_pos(window))
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE)
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
            elif action == glfw.RELEASE:
                self._isdrag = False
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.FALSE)
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def on_cursor_pos(self, window, x, y):
        p = ivec2(x, y)
        delta = p - self._prevpos
        self._prevpos = p
        if self._isdrag:
            win_pos = ivec2(*glfw.get_window_pos(window))
            glfw.set_window_pos(window, *(win_pos + delta))

    def update(self):
        self.uniform("u_time", glfw.get_time())
        self._render()

    def _render(self):
        self.va.render()

    # private:
    def _compile(self):
        try:
            p = self.gl.program(vertex_shader="""
#version 460
in vec4 in_pos;
out vec4 vs_pos;
void main() { vs_pos = in_pos; gl_Position = vs_pos; }
            """, fragment_shader="""
#version 460
in vec4 vs_pos;
out vec4 fs_colour;
uniform float u_time = 0.0;
void main()
{
vec2 uv = vs_pos.xy * 0.5 + 0.5;

float z = cos(u_time * 2.0) * 0.5 + 0.5;

fs_colour = vec4(uv, z, z);
}
            """)
            vb = self.gl.buffer(struct.pack("16f", -1.0, -1.0, 0.0, 1.0, +1.0, -1.0, 0.0, 1.0, -1.0, +1.0, 0.0, 1.0, +1.0, +1.0, 0.0, 1.0))
            ib = self.gl.buffer(struct.pack("6i", 0, 2, 1, 1, 2, 3))
            self.va = self.gl.vertex_array(p, [(vb, "4f", "in_pos")], ib)

            def uniform(n, v):
                if n in p:
                    p[n] = v

            self.uniform = uniform

        except Exception as e:
            print(e)


def main():
    glfw.init()

    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)

    window = glfw.create_window(1024, 1024, "", None, None)
    glfw.make_context_current(window)

    client = Client(window)
    client.init()

    while not glfw.window_should_close(window):
        glfw.swap_buffers(window)
        glfw.poll_events()
        client.update()


if __name__ == "__main__":
    main()
