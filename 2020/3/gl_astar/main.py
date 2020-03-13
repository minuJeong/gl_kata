import struct
from functools import partial

import glfw
import moderngl as mg
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


UP = vec3(0.0, 1.0, 0.0)
RIGHT = vec3(1.0, 0.0, 0.0)


def _uniform(p, n, v):
    if n in p:
        p[n] = v


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window

        self.gl = mg.create_context()
        self._compile()

        def on_mod(e):
            self._dirty = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_mod
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

        self._isdrag_camera = False
        self._isdrag_light = False
        self._isdrag_right = False
        self._isdrag_mid = False
        self._campos = vec3(-2.0, 3.0, -5.0)
        self._lightpos = vec3(-10.0, 20.0, -50.0)
        self._prevpos = (0, 0)

        _, _, w0, h0 = glfw.get_monitor_workarea(glfw.get_primary_monitor())
        w1, h1 = glfw.get_window_size(window)
        glfw.set_window_pos(window, w0 // 2 - w1 // 2, h0 // 2 - h1 // 2)
        glfw.set_framebuffer_size_callback(window, self.on_framebuffer_size)
        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)
        glfw.set_scroll_callback(window, self.on_scroll)

    def on_framebuffer_size(self, window, width, height):
        self.uniform("u_resolution", (width, height))
        self.gl.viewport = (0, 0, width, height)

    def on_mouse_button(self, window, button, action, mods):
        ispress = action == glfw.PRESS

        glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE if ispress else glfw.FALSE)
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED if ispress else glfw.CURSOR_NORMAL)

        if button == glfw.MOUSE_BUTTON_LEFT:
            if mods == glfw.MOD_SHIFT:
                self._isdrag_light = ispress
            elif mods == 0:
                self._isdrag_camera = ispress
        elif button == glfw.MOUSE_BUTTON_RIGHT:
            self._isdrag_right = ispress
        elif button == glfw.MOUSE_BUTTON_MIDDLE:
            self._isdrag_mid = ispress

    def on_cursor_pos(self, window, x, y):
        p = (x, y)
        dx, dy = p[0] - self._prevpos[0], p[1] - self._prevpos[1]
        self._prevpos = p

        # rotate camera
        if self._isdrag_camera:
            ru = rotate(mat4(1.0), -dx * 0.0005, UP)
            rr = rotate(mat4(1.0), dy * 0.0005, cross(self._campos, UP))
            p = (ru * rr) * vec4(self._campos, 1.0)
            self._campos = p.xyz

        if self._isdrag_light:
            ru = rotate(mat4(1.0), dx * 0.0005, UP)
            rr = rotate(mat4(1.0), -dy * 0.0005, cross(self._lightpos, UP))
            p = (ru * rr) * vec4(self._lightpos, 1.0)
            self._lightpos = p.xyz

        # zoom
        if self._isdrag_right:
            forward = normalize(-self._campos)
            next_pos = self._campos + forward * dx * 0.005
            self._campos = self._campos if length(next_pos) < 4.0 else next_pos

        # move window
        if self._isdrag_mid:
            wx, wy = glfw.get_window_pos(window)
            glfw.set_window_pos(window, int(wx + dx), int(wy + dy))

    def on_scroll(self, window, x, y):
        w, h = glfw.get_window_size(window)
        a = 1.1 if y > 0.0 else 0.9
        w, h = w * a, h * a
        w, h = int(clamp(w, 128, 4096)), int(clamp(h, 128, 4096))
        old_w, old_h = glfw.get_window_size(window)
        glfw.set_window_size(window, w, h)
        x, y = glfw.get_window_pos(window)
        glfw.set_window_pos(window, x - (w - old_w) // 2, y - (h - old_h) // 2)

    def _compile(self):
        self._dirty = False

        try:
            VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
            vb = self.gl.buffer(
                struct.pack(
                    "16f",
                    *(-1.0, -1.0, 0.0, 1.0),
                    *(+1.0, -1.0, 0.0, 1.0),
                    *(-1.0, +1.0, 0.0, 1.0),
                    *(+1.0, +1.0, 0.0, 1.0),
                )
            )
            ib = self.gl.buffer(struct.pack("6i", 0, 1, 2, 2, 1, 3))
            self.vao = self.gl.vertex_array(
                self.gl.program(vertex_shader=VS, fragment_shader=FS),
                [(vb, "4f", "in_pos")],
                ib,
            )
            self.uniform = partial(_uniform, self.vao.program)

            width, height = glfw.get_window_size(self.window)
            self.uniform("u_resolution", (width, height))

        except Exception as e:
            print(e)

    def update(self):
        if self._dirty:
            # skip a frame while compiling it
            self._compile()
            return

        self.uniform("u_campos", (*self._campos,))
        self.uniform("u_lightpos", (*self._lightpos,))
        self.gl.clear()
        self.vao.render()


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
    window = glfw.create_window(1280, 720, "window", None, None)
    glfw.make_context_current(window)

    client = Client(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
