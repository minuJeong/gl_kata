from glm import *
import glfw
import moderngl as mg
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from mesh import ScreenMesh
from scene import Pegasus, Minotaur


RIGHT = vec3(1.0, 0.0, 0.0)
UP = vec3(0.0, 1.0, 0.0)
FORWARD = vec3(0.0, 0.0, 1.0)


class ClientGLFW(object):
    def __init__(self, width, height, logger):
        super(ClientGLFW, self).__init__()

        self.logger = logger

        glfw.init()
        glfw.window_hint(glfw.FLOATING, glfw.TRUE)
        title = "client window"
        window = glfw.create_window(width, height, title, None, None)

        self.is_drag = False
        self.prev_cpos = vec2(0, 0)
        self.input_cam = vec2(0.0, 0.0)

        glfw.make_context_current(window)
        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)

        self.init()

        while not glfw.window_should_close(window):
            glfw.poll_events()
            glfw.swap_buffers(window)
            self.paint()

        glfw.terminate()

    def on_mouse_button(self, window, button, action, mods):
        if action == glfw.PRESS:
            if button == glfw.MOUSE_BUTTON_LEFT:
                self.prev_cpos = vec2(*glfw.get_cursor_pos(window))
                self.is_drag = True

        elif action == glfw.RELEASE:
            if button == glfw.MOUSE_BUTTON_LEFT:
                self.is_drag = False

    def on_cursor_pos(self, window, x, y):
        if self.is_drag:
            p = vec2(x, y)
            delta = p - self.prev_cpos
            self.prev_cpos = p

            self.input_cam.x += delta.x
            self.input_cam.y += delta.y

    def init(self):
        self.gl = mg.create_context()

        self.pegasus = Pegasus(self.gl)
        self.minotaur = Minotaur(self.gl)

        self.compile()

        self.view = mat4(1.0)
        self.perspective = perspective(radians(74.0), 1.0, 0.01, 100.0)

        def on_mod(e):
            self.should_recompile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_mod
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

    def compile(self):
        self.should_recompile = False
        try:
            vs, fs = "./gl/quad.vs", "./gl/quad.fs"
            self.bg = ScreenMesh(vs, fs)
            self.pegasus.compile()
            self.minotaur.compile()
            self.logger.info("compiled")

        except Exception as e:
            self.logger.error(e)

    def render(self):
        camdist = 8.0
        camerapos = vec3(2.0)
        camerapos.x = cos(self.input_cam.x * 0.002) * camdist
        camerapos.y = 2.0
        camerapos.z = sin(self.input_cam.x * 0.002) * camdist

        self.view = lookAt(camerapos, vec3(0.0, 2.0, 0.0), UP)
        VP = self.perspective * self.view

        self.gl.clear(red=0.2, green=0.2, blue=0.2, depth=100.0)
        self.gl.enable(mg.DEPTH_TEST)
        self.bg.render(self.gl, VP)

        self.pegasus.render(VP=VP)
        self.minotaur.render(VP=VP)

        self.gl.disable(mg.DEPTH_TEST)

    def paint(self):
        if self.should_recompile:
            self.compile()
            return

        self.render()


if __name__ == "__main__":
    import logging
    logger = logging.getLogger(__name__)
    width, height = 1024, 1024
    ClientGLFW(width, height, logger)
