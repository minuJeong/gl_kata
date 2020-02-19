import time

from glm import *
import numpy as np
import moderngl as mg
import imageio as ii
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.Qt import Qt
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


WIDTH, HEIGHT = 800, 800


class RenderWidget(QtWidgets.QOpenGLWidget):
    def __init__(self, tool):
        super(RenderWidget, self).__init__()

        self.setMinimumSize(WIDTH, HEIGHT)
        self.setMaximumSize(WIDTH, HEIGHT)

        self.alpha_value = 0.5
        self.hue_value = 0.5

        tool.alpha_value_update.connect(self.update_alpha_value)
        tool.hue_value_update.connect(self.update_hue_value)

    def initializeGL(self):
        self.gl = mg.create_context()

        self._compile_shaders()

        def onmod(e):
            self._need_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = onmod
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

    def _compile_shaders(self):
        self._need_compile = False

        try:
            VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)

            positions = (
                *vec4(-1.0, -1.0, 0.0, 1.0),
                *vec4(-1.0, +1.0, 0.0, 1.0),
                *vec4(+1.0, -1.0, 0.0, 1.0),
                *vec4(+1.0, +1.0, 0.0, 1.0),
            )
            vertices = self.gl.buffer(np.array(positions, dtype=np.float32))
            vertex_content = [(vertices, "4f", "in_pos")]
            indices = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))
            self.vao = self.gl.vertex_array(program, vertex_content, indices)

            img = ii.imread("./textures/base_colour.tga")
            self.base_colour_texture = self.gl.texture((img.shape[1], img.shape[0]), img.shape[2], img.tobytes())
            self.base_colour_texture.use(0)

            self._uniform("u_tex_aspect", img.shape[1] / img.shape[0])
            self._uniform("u_basecolour_tex", 0)

            self._uniform("u_slider_alpha", self.alpha_value)
            self._uniform("u_slider_hue", self.hue_value)

            print("compiled shaders")

        except Exception as e:
            print(e)

    def _uniform(self, uname, uvalue):
        if uname not in self.vao.program:
            return

        self.vao.program[uname] = uvalue

    def paintGL(self):
        if self._need_compile:
            self._compile_shaders()

        self._uniform("u_time", time.time() % 2000000.0)
        self.base_colour_texture.use(0)
        self.vao.render()
        self.update()

    @pyqtSlot(float)
    def update_alpha_value(self, value):
        self.alpha_value = value
        self._uniform("u_slider_alpha", self.alpha_value)

    @pyqtSlot(float)
    def update_hue_value(self, value):
        self.hue_value = value
        self._uniform("u_slider_hue", self.hue_value)


class Tool(QtWidgets.QMainWindow):
    alpha_value_update = pyqtSignal(float)
    hue_value_update = pyqtSignal(float)

    def __init__(self):
        super(Tool, self).__init__()

        self.setMinimumSize(WIDTH, HEIGHT)
        self.setMaximumSize(WIDTH, HEIGHT)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("RGB TO HUE DISPLAY")

        root_layout = QtWidgets.QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)

        root = QtWidgets.QWidget()
        root.setLayout(root_layout)
        self.setCentralWidget(root)

        # alpha slider
        alpha_slider_layout = QtWidgets.QHBoxLayout()
        alpha_slider_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.addLayout(alpha_slider_layout)

        self.label_alpha_slider = QtWidgets.QLabel("Alpha")
        self.label_alpha_slider.setMinimumWidth(100)
        alpha_slider_layout.addWidget(self.label_alpha_slider)

        slider_alpha = QtWidgets.QSlider()
        slider_alpha.setOrientation(Qt.Horizontal)
        slider_alpha.setMaximum(100)
        slider_alpha.valueChanged.connect(self.on_alpha_slider_changed)
        alpha_slider_layout.addWidget(slider_alpha)

        # hue slider
        hue_slider_layout = QtWidgets.QHBoxLayout()
        hue_slider_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.addLayout(hue_slider_layout)

        self.label_hue_slider = QtWidgets.QLabel("Hue")
        self.label_hue_slider.setMinimumWidth(100)
        hue_slider_layout.addWidget(self.label_hue_slider)

        slider_hue = QtWidgets.QSlider()
        slider_hue.setOrientation(Qt.Horizontal)
        slider_hue.setMaximum(100)
        slider_hue.valueChanged.connect(self.on_hue_slider_changed)
        hue_slider_layout.addWidget(slider_hue)

        # render widget
        render_widget = RenderWidget(self)
        root_layout.addWidget(render_widget)

    def on_alpha_slider_changed(self, value):
        self.label_alpha_slider.setText(f"Alpha: {value / 10.0}")
        self.alpha_value_update.emit(float(value) / 10.0)

    def on_hue_slider_changed(self, value):
        self.label_hue_slider.setText(f"Hue: {value / 100.0}")
        self.hue_value_update.emit(float(value) / 100.0)


def main():
    app = QtWidgets.QApplication([])
    tool = Tool()
    tool.show()
    app.exec()


if __name__ == "__main__":
    main()
