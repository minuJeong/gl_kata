import time

from glm import *
import moderngl as mg
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import Qt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from mesh import ScreenMesh
from scene import Pegasus, Minotaur


UP = vec3(0.0, 1.0, 0.0)


class _RenderWidget(QtWidgets.QOpenGLWidget):
    move_signal = pyqtSignal(vec2)

    def __init__(self, width, height, logger):
        super(_RenderWidget, self).__init__()

        self.width, self.height = width, height

        self.setMinimumSize(width, height)
        self.setMaximumSize(width, height)

        self.logger = logger

        self.is_drag_left = False
        self.is_drag_middle = False
        self.prevpos = vec2(0.0, 0.0)

        self.setMouseTracking(True)

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

        self.logger.info("initializeGL")

    def compile(self):
        self.should_recompile = False
        try:
            self.bg = ScreenMesh("./gl/quad.vs", "./gl/quad.fs")
            self.pegasus.compile()
            self.minotaur.compile()
            self.logger.info("compiled")

        except Exception as e:
            self.logger.error(e)

    def resizeGL(self, width, height):
        self.width, self.height = width, height
        self.gl.viewport = (0, 0, width, height)

    def render(self):
        t = time.time() % 100000.0

        camdist = 10.0
        camerapos = vec3(2.0)
        camerapos.x = cos(t) * camdist
        camerapos.z = sin(t) * camdist

        self.view = lookAt(camerapos, vec3(0.0, 2.0, 0.0), UP)
        VP = self.perspective * self.view

        self.gl.enable(mg.DEPTH_TEST)
        self.bg.render(self.gl, VP)
        self.pegasus.render(VP=VP)
        self.minotaur.render(VP=VP)
        self.gl.disable(mg.DEPTH_TEST)

    def paintGL(self):
        if self.should_recompile:
            self.compile()

        self.render()
        self.update()

    def mousePressEvent(self, e):
        self.prevpos = vec2(e.globalPos().x(), e.globalPos().y())

        if e.button() == Qt.LeftButton:
            self.is_drag_left = True

        elif e.button() == Qt.MiddleButton:
            self.is_drag_middle = True

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.is_drag_left = False

        elif e.button() == Qt.MiddleButton:
            self.is_drag_middle = False

    def mouseMoveEvent(self, e):
        pos = vec2(e.globalPos().x(), e.globalPos().y())
        delta = pos - self.prevpos
        self.prevpos = pos

        if self.is_drag_left:
            pass

        elif self.is_drag_middle:
            self.move_signal.emit(delta)


class QCustomButton(QtWidgets.QPushButton):
    def __init__(self):
        super(QCustomButton, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.clicked.connect(self.on_click)

    @pyqtSlot(bool)
    def on_click(self, e=None):
        """ override this method to implement click behaviour """
        print("clicked")


class QButtonFromMaxScene(QCustomButton):
    def __init__(self):
        super(QButtonFromMaxScene, self).__init__()
        self.setText("From Max Scene")

    @pyqtSlot(bool)
    def on_click(self, e=None):
        pass


class QButtonToMaxScene(QCustomButton):
    def __init__(self):
        super(QButtonToMaxScene, self).__init__()
        self.setText("To Max Scene")

    @pyqtSlot(bool)
    def on_click(self, e=None):
        pass


class _Tool(QtWidgets.QMainWindow):
    on_loaded_signal = pyqtSignal()

    def __init__(self, width, height, logger):
        super(_Tool, self).__init__()

        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Communication with 3ds Max")

        root = QtWidgets.QWidget()
        self.setCentralWidget(root)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        root.setLayout(layout)

        renderer = _RenderWidget(width, height, logger)
        layout.addWidget(renderer)

        layout_buttons = QtWidgets.QHBoxLayout()
        layout_buttons.setSpacing(0)
        layout_buttons.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(layout_buttons)

        button_from_max = QButtonFromMaxScene()
        layout_buttons.addWidget(button_from_max)
        button_to_max = QButtonToMaxScene()
        layout_buttons.addWidget(button_to_max)

        renderer.move_signal.connect(self.on_renderer_move)

    def showEvent(self, e):
        self.on_loaded_signal.emit()

    def on_renderer_move(self, pos):
        print(pos, self.pos())
        cur_pos = vec2(self.x(), self.y())
        self.setGeometry(*(cur_pos - pos).xy, self.width(), self.height())


class _Splash(QtWidgets.QLabel):
    def __init__(self, tool):
        super(_Splash, self).__init__()
        tool.on_loaded_signal.connect(self.on_loaded)

        self.setWindowFlag(Qt.SplashScreen)
        self.setPixmap(QPixmap("./res/splash.png"))

    def on_loaded(self):
        self.close()


class ClientPYQT5(object):
    def __init__(self, width, height, logger):
        super(ClientPYQT5, self).__init__()

        app = QtWidgets.QApplication([])
        tool = _Tool(width, height, logger)
        splash = _Splash(tool)
        splash.show()
        tool.show()
        app.exec()


if __name__ == "__main__":
    import logging
    logger = logging.getLogger(__name__)
    width, height = 1024, 1024
    ClientPYQT5(width, height, logger)
