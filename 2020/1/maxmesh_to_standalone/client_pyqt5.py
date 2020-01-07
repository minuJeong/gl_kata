from glm import *
import moderngl as mg
from PyQt5 import QtWidgets
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from scene import Pegasus, Minotaur


class _RenderWidget(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(_RenderWidget, self).__init__()

    def compile(self):
        self.should_recompile = False
        try:
            vs, fs = "./gl/quad.vs", "./gl/quad.fs"
            self.bg = ScreenMesh(vs, fs)

            self.pegasus.compile(self.gl)
            self.minotaur.compile(self.gl)

            logger.info("compiled")

        except Exception as e:
            logger.error(e)

    def initializeGL(self):
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

    def render(self):
        t = time.time() % 100000.0

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

    def paintGL(self):
        if self.should_recompile:
            self.compile()
            return

        self.render()


class _Tool(QtWidgets.QMainWindow):
    def __init__(self):
        super(_Tool, self).__init__()

        root = QtWidgets.QWidget()
        self.setCentralWidget(root)
        layout = QtWidgets.QVBoxLayout()
        root.setlayout(layout)

        renderer = _RenderWidget()
        layout.addWidget(renderer)


class ClientPYQT5(object):
    def __init__(self, framework):
        super(ClientPYQT5, self).__init__()

        app = QtWidgets.QApplication([])
        tool = _Tool()
        tool.show()
        app.exec()
