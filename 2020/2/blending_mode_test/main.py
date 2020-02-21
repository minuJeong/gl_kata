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

from custom_widgets import QColorPropertyPicker


WIDTH, HEIGHT = 800, 800


class RenderWidget(QtWidgets.QOpenGLWidget):
    def __init__(self, tool):
        super(RenderWidget, self).__init__()

        self.setMinimumSize(WIDTH, HEIGHT)
        self.setMaximumSize(WIDTH, HEIGHT)

        # init values
        self.mask_type_value = 0
        self.alpha_value = 1.0
        self.colour_value = vec4(1.0, 1.0, 1.0, 1.0)
        self.blendmode_value = 3

        tool.mask_type_update.connect(self.update_mask_type)
        tool.alpha_value_update.connect(self.update_alpha_value)
        tool.colour_value_update.connect(self.update_colour_value)
        tool.blendmode_update.connect(self.update_blendmode)

    def initializeGL(self):
        self.gl = mg.create_context()
        self._compile_shaders()

        def onmod(e):
            self._need_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = onmod
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.schedule(handler, "./textures", True)
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

            # reset to latest setting from tool interface
            self._uniform("u_masktype", self.mask_type_value)
            self._uniform("u_slider_alpha", self.alpha_value)
            self._uniform("u_colour_picker", (*self.colour_value,))
            self._uniform("u_blendmode", self.blendmode_value)

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

    @pyqtSlot(int)
    def update_mask_type(self, value):
        self.mask_type_value = value
        self._uniform("u_masktype", value)

    @pyqtSlot(float)
    def update_alpha_value(self, value):
        self.alpha_value = value
        self._uniform("u_slider_alpha", self.alpha_value)

    @pyqtSlot(vec4)
    def update_colour_value(self, value):
        self.colour_value = value
        self._uniform("u_colour_picker", (*self.colour_value,))

    @pyqtSlot(int)
    def update_blendmode(self, value):
        self.blendmode_value = value
        self._uniform("u_blendmode", self.blendmode_value)


class Tool(QtWidgets.QMainWindow):
    mask_type_update = pyqtSignal(int)
    alpha_value_update = pyqtSignal(float)
    colour_value_update = pyqtSignal(vec4)
    blendmode_update = pyqtSignal(int)

    # TODO: ADD COLOUR PICKER

    def __init__(self):
        super(Tool, self).__init__()

        self.setMinimumSize(WIDTH, HEIGHT)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Uniform Tinting Shader Prototype")

        root_layout = QtWidgets.QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)

        root = QtWidgets.QWidget()
        root.setLayout(root_layout)
        self.setCentralWidget(root)

        # preferences [TBD]
        group_preferences = QtWidgets.QGroupBox()
        group_preferences.setTitle("Preferences")

        preferences_layout = QtWidgets.QHBoxLayout()
        group_preferences.setLayout(preferences_layout)
        # root_layout.addWidget(group_preferences)

        # mask selector
        group_mask_type_select = QtWidgets.QGroupBox()
        group_mask_type_select.setTitle("Mask Type")

        mask_type_select_layout = QtWidgets.QGridLayout()
        group_mask_type_select.setLayout(mask_type_select_layout)
        root_layout.addWidget(group_mask_type_select)

        columns = 5
        mask_names = [
            *("truchet &0", "truchet &1", "truchet &2", "truchet &3", "truchet &4"),
            *("&cloud", "&fluid", "oil 0", "oil 1", "oil 2"),
            *("fla&t fill", "flat &empty", "checke&r",),
        ]
        self.mask_radio = {}
        for i in range(13):
            radio_mask = QtWidgets.QRadioButton()
            radio_mask.setMinimumHeight(60)
            self.mask_radio[i] = radio_mask
            radio_mask.setStyleSheet("background: #DDD" if i % 2 == 0 else "background: #FFF")
            radio_mask.setChecked(i == 0)
            radio_mask.setText(mask_names[i] if i < len(mask_names) else f"mask {i}")
            radio_mask.toggled.connect(self.on_select_mask_type)
            mask_type_select_layout.addWidget(radio_mask, int(floor(i / columns)), int(mod(i, columns)))

        # alpha slider
        alpha_slider_layout = QtWidgets.QHBoxLayout()
        alpha_slider_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.addLayout(alpha_slider_layout)

        self.label_alpha_slider = QtWidgets.QLabel("Alpha: 100% / 400%")
        self.label_alpha_slider.setMinimumWidth(200)
        alpha_slider_layout.addWidget(self.label_alpha_slider)

        slider_alpha = QtWidgets.QSlider()
        slider_alpha.setOrientation(Qt.Horizontal)
        slider_alpha.setMaximum(400)
        slider_alpha.setValue(100)
        slider_alpha.valueChanged.connect(self.on_alpha_slider_changed)
        alpha_slider_layout.addWidget(slider_alpha)
        self.on_alpha_slider_changed(slider_alpha.value())

        # coloiur picker
        colour_pick_layout = QtWidgets.QHBoxLayout()
        colour_pick_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.addLayout(colour_pick_layout)

        label_colour_picker = QtWidgets.QLabel("Faction Colour")
        label_colour_picker.setMinimumWidth(200)
        colour_pick_layout.addWidget(label_colour_picker)

        colour_picker_container = QtWidgets.QWidget()
        colour_pick_layout.addWidget(colour_picker_container)
        cp_container_layout = QtWidgets.QHBoxLayout()
        colour_picker_container.setLayout(cp_container_layout)

        colour_picker = QColorPropertyPicker()
        colour_picker.color_picked_signal.connect(self.on_colour_picked)
        cp_container_layout.addWidget(colour_picker)

        # blend mode combo box
        blendmode_layout = QtWidgets.QHBoxLayout()
        blendmode_layout.setContentsMargins(10, 10, 10, 10)

        label_blendmode = QtWidgets.QLabel("Blend Mode")
        label_blendmode.setMinimumWidth(200)
        label_blendmode.setMaximumWidth(200)
        blendmode_layout.addWidget(label_blendmode)

        cb_blendmode = QtWidgets.QComboBox()
        cb_blendmode.addItem("Normal")
        cb_blendmode.addItem("Multiply")
        cb_blendmode.addItem("Overlay")
        cb_blendmode.addItem("Hue")
        cb_blendmode.addItem("Soft Light")
        cb_blendmode.setCurrentIndex(3)
        cb_blendmode.currentIndexChanged.connect(self.on_blendmode_change)
        blendmode_layout.addWidget(cb_blendmode)
        self.on_blendmode_change(cb_blendmode.currentIndex())

        root_layout.addLayout(blendmode_layout)

        # render widget
        render_widget = RenderWidget(self)
        root_layout.addWidget(render_widget)

    def on_select_mask_type(self, value):
        for idx, radio in self.mask_radio.items():
            if radio.isChecked():
                self.mask_type_update.emit(idx)
                return
        self.mask_type_update.emit(0)

    def on_alpha_slider_changed(self, value):
        self.label_alpha_slider.setText(f"Alpha: {value}% / 400%")
        self.alpha_value_update.emit(float(value) / 100.0)

    def on_colour_picked(self, value):
        self.colour_value_update.emit(value)

    def on_blendmode_change(self, value):
        self.blendmode_update.emit(value)


def main():
    app = QtWidgets.QApplication([])
    tool = Tool()
    tool.show()
    app.exec()


if __name__ == "__main__":
    main()
