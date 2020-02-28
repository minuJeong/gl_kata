import glfw
import moderngl as mg
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from mesh import Background, Cube, SnakeQuads, DeferredLight


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window

        self.is_drag = False
        self.last_pos = ivec2(0, 0)

        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)
        glfw.set_key_callback(window, self.on_key)

    def on_mouse_button(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_MIDDLE:
            if action == glfw.PRESS:
                self.last_pos = ivec2(*glfw.get_cursor_pos(window))
                self.is_drag = True
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE)
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
            elif action == glfw.RELEASE:
                self.is_drag = False
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.FALSE)
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def on_cursor_pos(self, window, x, y):
        pos = ivec2(x, y)
        delta = pos - self.last_pos
        self.last_pos = pos

        if self.is_drag:
            win_pos = ivec2(*glfw.get_window_pos(window))
            glfw.set_window_pos(window, *(win_pos + delta))

    def on_key(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE:
            if action == glfw.RELEASE:
                glfw.set_window_should_close(window, glfw.TRUE)

    def update(self):
        raise NotImplemented


class RenderClient(Client):
    def __init__(self, window):
        super(RenderClient, self).__init__(window)
        self.gl = mg.create_context()
        self._compile()

        def on_mod(e):
            self._need_compile = True

        hand = FileSystemEventHandler()
        hand.on_modified = on_mod
        o = Observer()
        o.schedule(hand, "./gl/", True)
        o.start()

    def _compile(self):
        self._need_compile = False

        try:
            gl = self.gl
            self.scene = []
            self.scene.extend(
                [Background(gl), Cube(gl), SnakeQuads(gl), DeferredLight(gl)]
            )
            print("compiled")

        except Exception as e:
            raise "X"
            print(e)

    def update(self):
        if self._need_compile:
            self._compile()

        self.gl.clear()
        for node in self.scene:
            node.render()


if __name__ == "__main__":
    from main import main

    main()
