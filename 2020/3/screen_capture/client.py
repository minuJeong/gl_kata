import struct
from functools import partial

import glfw
import numpy as np
import moderngl as mg
import imageio as ii

from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from const import _uniform


class WindowClient(object):
    def __init__(self, window):
        super(WindowClient, self).__init__()

        self.window = window

        m = glfw.get_primary_monitor()
        _, _, w, h = glfw.get_monitor_workarea(m)
        ww, wh = glfw.get_window_size(window)
        glfw.set_window_pos(window, w // 2 - ww // 2, h // 2 - wh // 2)

        self._isdrag = False
        self._prevpos = ivec2(0, 0)

        glfw.set_framebuffer_size_callback(self.window, self.on_framebuffer_size)
        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)

    def on_framebuffer_size(self, window, w, h):
        pass

    def on_window_move(self):
        pass

    def on_start_drag(self):
        pass

    def on_mouse_button(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_MIDDLE:
            if action == glfw.PRESS:
                self._isdrag = True
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE)
                self.on_start_drag()
            elif action == glfw.RELEASE:
                self._isdrag = False
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.FALSE)
                self.on_window_move()

    def on_cursor_pos(self, window, x, y):
        p = ivec2(x, y)
        d = p - self._prevpos
        self._prevpos = p
        if self._isdrag:
            win_pos = ivec2(*glfw.get_window_pos(window))
            win_pos += d
            glfw.set_window_pos(window, *win_pos)


class Client(WindowClient):
    def __init__(self, window):
        super(Client, self).__init__(window)
        self.init()

    def init(self):
        self.gl = mg.create_context()

        self._compile()

        handler = FileSystemEventHandler()
        handler.on_modified = lambda e: self.set_need_compile(True)
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

        self.on_framebuffer_size(self.window, *glfw.get_window_size(self.window))

    def on_mouse_button(self, window, button, action, mods):
        super(Client, self).on_mouse_button(window, button, action, mods)

        if not hasattr(self, "uniform"):
            return

        if action == glfw.PRESS:
            self.uniform(f"u_ispress_{button}", 1.0)
        elif action == glfw.RELEASE:
            self.uniform(f"u_ispress_{button}", 0.0)
            if button == glfw.MOUSE_BUTTON_RIGHT:
                self._need_capture = True

    def on_framebuffer_size(self, window, w, h):
        if h > 0:
            self.uniform("u_res", (w, h))
            self.uniform("u_aspect", w / h)
            self.gl.viewport = (0, 0, w, h)

    def set_need_compile(self, value):
        self._need_compile = value

    def _compile(self):
        self._need_compile = False
        self._need_capture = False
        self.scene = []

        try:
            VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
            program_forward = self.gl.program(vertex_shader=VS, fragment_shader=FS)

            p, q = vec4(-1.0, -1.0, 0.0, 1.0), vec4(+1.0, -1.0, 0.0, 1.0)
            s, t = vec4(-1.0, +1.0, 0.0, 1.0), vec4(+1.0, +1.0, 0.0, 1.0)
            vb = self.gl.buffer(struct.pack("16f", *p, *q, *s, *t))
            ib = self.gl.buffer(struct.pack("6i", 0, 1, 2, 2, 1, 3))
            self.scene.append(
                self.gl.vertex_array(program_forward, [(vb, "4f", "in_pos")], ib)
            )

            FS_DEFERRED = open("./gl/fs_deferred.glsl").read()
            program_deferred = self.gl.program(vertex_shader=VS, fragment_shader=FS_DEFERRED)
            self.deferred = self.gl.vertex_array(
                program_deferred, [(vb, "4f", "in_pos")], ib
            )

            programs = [program_forward, program_deferred]

            def uniform_comb(uname, uvalue):
                for program in programs:
                    partial(_uniform, program)(uname, uvalue)

            self.uniform = uniform_comb

            w, h = glfw.get_window_size(self.window)

            self.color_tex = self.gl.texture((w, h), 4)
            self.color_tex.use(1)
            self.depth_tex = self.gl.depth_texture((w, h))
            self.gbuffer = self.gl.framebuffer([self.color_tex], self.depth_tex)

            self.screen_tex = self.gl.texture((w, h), 3)
            self.capture()

            self.on_framebuffer_size(self.window, *glfw.get_window_size(self.window))
            print("compiled")

        except Exception as e:
            print(e)

    def capture(self):
        self._need_capture = False

        screen_img = ii.imread("<screen>")
        x, y = glfw.get_window_pos(self.window)
        w, h = glfw.get_window_size(self.window)

        sw, sh = screen_img.shape[1], screen_img.shape[0]
        x, y = int(min(max(x, 0), sw - x)), int(min(max(y, 0), sh - y))

        canvas_img = np.zeros((h, w, 3), dtype=np.ubyte)
        canvas_img[0: h, 0: w] = screen_img[y: y + h, x: x + w]

        self.screen_tex.write(canvas_img.tobytes())
        self.screen_tex.use(0)

    def update(self):
        if self._need_compile:
            self._compile()

        self.uniform("u_time", glfw.get_time())
        self.uniform("u_mousepos", glfw.get_cursor_pos(self.window))

        self.gbuffer.use()
        for node in self.scene:
            node.render()

        self.gl.screen.use()
        self.deferred.render()

        if self._need_capture:
            self.capture()


if __name__ == "__main__":
    from main import main

    main()
