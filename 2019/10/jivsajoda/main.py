import moderngl as mg
import glfw
from glm import *

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from util import Loader


class Program(object):
    def __init__(self, gl):
        super(Program, self).__init__()
        self.gl = gl
        self.vs = None
        self.fs = None

    def setpath(self, vspath, fspath):
        self.vspath, self.fspath = vspath, fspath
        self.vs = None
        self.fs = None

    def read_file(self):
        if not self.vs:
            self.vs = Loader.shader(self.vspath)

        if not self.fs:
            self.fs = Loader.shader(self.fspath)

    def compile(self):
        self.read_file()
        p = self.gl.program(vertex_shader=self.vs, fragment_shader=self.fs)
        return p


class Renderer(object):
    def __init__(self):
        super(Renderer, self).__init__()

    def main(self):
        self.drag_offset = ivec2(0.0, 0.0)
        self.drag_start_winpos = ivec2(0.0, 0.0)
        self.is_drag = False

        glfw.init()
        glfw.window_hint(glfw.FLOATING, glfw.TRUE)
        glfw.window_hint(glfw.DECORATED, glfw.FALSE)
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)

        self.width, self.height = 512, 512
        self.window = glfw.create_window(
            self.width, self.height, "render_0", None, None
        )

        x, y, w, h = glfw.get_monitor_workarea(glfw.get_primary_monitor())
        glfw.set_window_pos(self.window, (w - self.width) >> 1, (h - self.height) >> 1)
        glfw.make_context_current(self.window)

        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(self.window, self.on_cursor_pos)
        glfw.set_key_callback(self.window, self.on_key)

        self.init_gl()

        handler = FileSystemEventHandler()
        handler.on_modified = self.on_modified
        observer = Observer()
        observer.schedule(handler, "./gl/", True)
        observer.start()

        while not glfw.window_should_close(self.window):
            if self.should_recomile:
                self.compile_vao()

            self.paint_gl()
            glfw.swap_buffers(self.window)
            glfw.poll_events()

    def start_drag(self):
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_HIDDEN)
        wx, wy = glfw.get_window_pos(self.window)
        cx, cy = glfw.get_cursor_pos(self.window)
        self.drag_start_winpos = ivec2(wx, wy)
        self.drag_offset = ivec2(cx, cy)
        self.is_drag = True

    def stop_drag(self):
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)
        self.is_drag = False

    def on_mouse_button(self, w, button, action, mods):
        if button == glfw.MOUSE_BUTTON_RIGHT:
            if action == glfw.PRESS:
                self.start_drag()

            elif action == glfw.RELEASE:
                self.stop_drag()

    def on_cursor_pos(self, w, x, y):
        if not self.is_drag:
            return

        wx, wy = glfw.get_window_pos(self.window)
        glfw.set_window_pos(
            self.window,
            int(wx + x - self.drag_offset.x),
            int(wy + y - self.drag_offset.y),
        )

    def on_key(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(self.window, glfw.TRUE)

    def on_modified(self, e):
        self.should_recomile = True

    def init_gl(self):
        self.gl = mg.create_context()
        self.program = Program(self.gl)
        self.vbo = self.gl.buffer(
            bytes(vec2(-1.0, -1.0))
            + bytes(vec2(-1.0, +1.0))
            + bytes(vec2(+1.0, -1.0))
            + bytes(vec2(+1.0, +1.0))
        )

        self.ibo = self.gl.buffer(bytes(ivec3(0, 1, 2)) + bytes(ivec3(2, 1, 3)))

        self.compile_vao()

    def compile_vao(self):
        self.should_recomile = False
        try:
            self.program.setpath(vspath="./gl/vertex.glsl", fspath="./gl/fragment.glsl")
            self.vao = self.gl.vertex_array(
                self.program.compile(), [(self.vbo, "2f", "in_pos")], self.ibo
            )
            print("vao compiled")

        except Exception as e:
            print(e)

    def paint_gl(self):
        self.gl.clear(alpha=0.0)
        self.gl.enable(mg.BLEND)
        self.vao.render()


def main():
    control_0 = Renderer()
    control_0.main()


if __name__ == "__main__":
    main()
