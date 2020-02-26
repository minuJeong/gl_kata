import glfw
import moderngl as mg
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from mesh import Mesh


scene_def = [
    (
        "./gl/mesh/mesh_builder_0.glsl",
        "./gl/mesh/mesh_updater_0.glsl",
        "./gl/vs/vs_0.glsl",
        "./gl/fs/fs_0.glsl",
    ),
]


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()

        self.is_drag = False
        self.prev_pos = ivec2(0, 0)

        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)

    def on_mouse_button(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_MIDDLE:
            if action == glfw.PRESS:
                self.is_drag = True
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE)
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                self.prev_pos = ivec2(glfw.get_cursor_pos(window))

            elif action == glfw.RELEASE:
                self.is_drag = False
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.FALSE)
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def on_cursor_pos(self, window, x, y):
        pos = ivec2(x, y)
        d = pos - self.prev_pos
        self.prev_pos = pos

        if self.is_drag:
            new_pos = ivec2(glfw.get_window_pos(window)) + d
            glfw.set_window_pos(window, *new_pos)


class RenderClient(Client):
    def __init__(self, window):
        super(RenderClient, self).__init__(window)

        self.gl = mg.create_context()
        self.compile()

        hand = FileSystemEventHandler()
        hand.on_modified = lambda e: self.set_need_compile()
        observer = Observer()
        observer.schedule(hand, "./gl", True)
        observer.start()

    def set_need_compile(self):
        self._need_compile = True

    def compile(self):
        self._need_compile = False
        try:
            self.scene = []

            for node in scene_def:
                assert len(node) == 4
                mesh = Mesh(self.gl, *node)
            self.scene.append(mesh)

            print("compiled")

        except Exception as e:
            print(e)

    def uniform(self, uname, uvalue):
        for node in self.scene:
            node.uniform(uname, uvalue)

    def update(self):
        if self._need_compile:
            self.compile()

        self.uniform("u_time", glfw.get_time())

        self.gl.clear()
        self.gl.enable(mg.DEPTH_TEST)
        # self.gl.enable(mg.CULL_FACE)
        for node in self.scene:
            node.render()

if __name__ == "__main__":
    from main import main
    main()
