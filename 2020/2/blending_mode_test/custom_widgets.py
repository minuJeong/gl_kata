from glm import *
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSignal


class QColorPropertyPicker(QtWidgets.QPushButton):
    color_picked_signal = pyqtSignal(vec4)

    def __init__(self, init_value=vec4(0.0, 0.0, 0.0, 1.0)):
        super(QColorPropertyPicker, self).__init__()

        if isinstance(init_value, vec3):
            init_value = vec4(init_value, 1.0)

        self.setAutoFillBackground(True)
        self.color = init_value

        self.setFlat(True)
        self.update_widget_color()

        self.clicked.connect(self.on_query_color)

        self.setMinimumSize(50, 50)
        self.setMaximumSize(50, 50)

    def update_widget_color(self):
        r, g, b, a = self.color
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        r, g, b = min(max(r, 0), 255), min(max(g, 0), 255), min(max(b, 0), 255)
        color = QtGui.QColor(r, g, b)
        palette = QtGui.QPalette()

        palette.setColor(QtGui.QPalette.Button, color)
        palette.setColor(QtGui.QPalette.BrightText, color)

        self.setPalette(palette)

    def on_query_color(self, e):
        self.color_dialog = QtWidgets.QColorDialog()
        self.color_dialog.setModal(True)
        self.color_dialog.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.color_dialog.show()
        self.color_dialog.colorSelected.connect(self.on_color_selected)

    def on_color_selected(self, color):
        r, g, b, a = color.getRgb()
        r, g, b, a = r / 255.0, g / 255.0, b / 255.0, a / 255.0

        self.color_picked_signal.emit(vec4(r, g, b, a))
        self.color = vec4(r, g, b, a)
        self.update_widget_color()

    def get_color(self):
        return self.color
