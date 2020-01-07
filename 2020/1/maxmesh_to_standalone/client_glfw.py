from glm import *
import glfw
import moderngl as mg
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from mesh import ScreenMesh
from scene import Pegasus, Minotaur


UP = vec3(0.0, 1.0, 0.0)


class ClientGLFW(object):
    def __init__(self, width, height, logger):
        super(ClientGLFW, self).__init__()

        self.logger = logger

        glfw.init()
        glfw.window_hint(glfw.FLOATING, glfw.TRUE)
        title = "client window"
        window = glfw.create_window(width, height, title, None, None)
        glfw.make_context_current(window)

        self.init()

        while not glfw.window_should_close(window):
            glfw.poll_events()
            glfw.swap_buffers(window)
            self.paint()

        glfw.terminate()

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

            self.pegasus.compile(self.gl)
            self.minotaur.compile(self.gl)

            self.logger.info("compiled")

        except Exception as e:
            self.logger.error(e)

    def render(self):
        t = glfw.get_time()

        camdist = 10.0
        camerapos = vec3(2.0)
        camerapos.x = cos(t) * camdist
        camerapos.z = sin(t) * camdist

        self.view = lookAt(camerapos, vec3(0.0, 2.0, 0.0), UP)

        self.gl.clear(red=0.2, green=0.2, blue=0.2, depth=100.0)
        VP = self.perspective * self.view

        self.gl.enable(mg.DEPTH_TEST)
        self.bg.render(self.gl, VP)
        self.pegasus.render(self.gl, VP)
        self.minotaur.render(self.gl, VP)
        self.gl.disable(mg.DEPTH_TEST)

    def paint(self):
        if self.should_recompile:
            self.compile()
            return

        self.render()
