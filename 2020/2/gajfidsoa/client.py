import glfw
import numpy as np
import moderngl as mg
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from mesh import Mesh, MeshDef


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window

        self.is_drag = False
        self.prev_pos = ivec2(0, 0)

        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)

    def on_mouse_button(self, window, button, action, mods):
        if action == glfw.PRESS:
            if button == glfw.MOUSE_BUTTON_MIDDLE:
                self.is_drag = True
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE)
                self.prev_pos = ivec2(glfw.get_cursor_pos(window))
        elif action == glfw.RELEASE:
            if button == glfw.MOUSE_BUTTON_MIDDLE:
                self.is_drag = False
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.FALSE)

    def on_cursor_pos(self, window, x, y):
        pos = ivec2(x, y)
        d = pos - self.prev_pos
        self.prev_pos = pos

        if self.is_drag:
            win_pos = ivec2(*glfw.get_window_pos(window))
            glfw.set_window_pos(window, *(win_pos + d))

    def update(self):
        raise Exception("update is not overriden")


class RenderClient(Client):
    def __init__(self, window):
        super(RenderClient, self).__init__(window)

        self.gl = mg.create_context()
        self._compile()

        def set_need_compile():
            self._need_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = lambda e: set_need_compile()
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

    def _compile(self):
        self._need_compile = False

        try:
            p, q = vec4(-1.0, -1.0, 0.0, 1.0), vec4(+1.0, -1.0, 0.0, 1.0)
            s, t = vec4(-1.0, +1.0, 0.0, 1.0), vec4(+1.0, +1.0, 0.0, 1.0)
            mesh_def = MeshDef(
                *("./gl/vs.glsl", "./gl/fs.glsl"),
                np.array((*p, *q, *s, *t), dtype=np.float32),
                np.array([0, 1, 2, 2, 1, 3], dtype=np.int32)
            )
            self.scene = [Mesh(self.gl, mesh_def)]

        except Exception as e:
            print(e.with_traceback(None))

    def update(self):
        if self._need_compile:
            self._compile()

        self.gl.enable(mg.BLEND)
        for node in self.scene:
            node.render()


if __name__ == "__main__":
    from main import main

    main()
