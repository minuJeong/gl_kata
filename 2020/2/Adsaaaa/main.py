import glfw
import moderngl as mg
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from const import WIDTH, HEIGHT, TITLE
from mesh import BackgroundMesh


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window

        self._is_drag = False
        self._pre_cursor = ivec2(0, 0)

        monitor = glfw.get_primary_monitor()
        x, y, w, h = glfw.get_monitor_workarea(monitor)
        ww, wh = glfw.get_window_size(window)
        glfw.set_window_pos(window, (w >> 1) - (ww >> 1), (h >> 1) - (wh >> 1))

        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)

    def on_mouse_button(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_MIDDLE:
            if action == glfw.PRESS:
                self._is_drag = True
                self._pre_cursor = ivec2(*glfw.get_cursor_pos(window))
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE)
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
            elif action == glfw.RELEASE:
                self._is_drag = False
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.FALSE)
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def on_cursor_pos(self, window, x, y):
        pos = ivec2(x, y)
        delta = pos - self._pre_cursor
        self._pre_cursor = pos

        if self._is_drag:
            win_pos = ivec2(*glfw.get_window_pos(window))
            glfw.set_window_pos(window, *(win_pos + delta))

    def update(self):
        raise NotImplemented


class RenderingClient(Client):
    def __init__(self, window):
        super(RenderingClient, self).__init__(window)

        self.gl = mg.create_context()
        self._compile_shaders()

        def set_need_compile():
            self._need_compile = True

        hand = FileSystemEventHandler()
        hand.on_modified = lambda e: set_need_compile()
        obs = Observer()
        obs.schedule(hand, "./gl/", True)
        obs.start()

    def _compile_shaders(self):
        self._need_compile = False
        try:
            self.scene = []
            self.scene.append(BackgroundMesh(self.gl))
            w, h = glfw.get_window_size(self.window)
            self.uniform("u_screen_aspect", w / h)

        except Exception as e:
            print(e)

    def uniform(self, uname, uvalue):
        for node in self.scene:
            node.uniform(uname, uvalue)

    def update(self):
        if self._need_compile:
            self._compile_shaders()

        self.uniform("u_time", glfw.get_time())
        self.gl.clear()
        for node in self.scene:
            node.render()


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    window = glfw.create_window(WIDTH, HEIGHT, TITLE, None, None)
    glfw.make_context_current(window)
    client = RenderingClient(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
