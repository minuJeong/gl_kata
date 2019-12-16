import time

from glm import *
import moderngl as mg
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.Qt import Qt
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def read(path, mode="r"):
    with open(path, mode) as fp:
        return fp.read()


class ControlledProperty(object):
    uname = "u_notset"
    is_dirty = False
    value = None
    default_value = None
    target_type = type(None)

    def __init__(self, uname, default_value=None):
        super(ControlledProperty, self).__init__()
        self.default_value = self.default_value or default_value
        self.uname = uname
        self.value = self.default_value

    def set(self, value):
        assert isinstance(value, self.target_type)
        self.is_dirty = True
        self.value = value

    def get(self):
        self.is_dirty = False
        return self.uname, self.value


class ControlledFloat(ControlledProperty):
    target_type = float
    default_value = 0.0


class ControlledBool(ControlledProperty):
    target_type = bool
    default_value = False


class ControlledVec2(ControlledProperty):
    target_type = vec2
    default_value = vec2(0.0)


class ControlledVec3(ControlledProperty):
    target_type = vec3
    default_value = vec3(0.0)


class QRenderWidget(QtWidgets.QOpenGLWidget):
    u_slider_value = ControlledVec3("u_slider_pos", vec3(0.0))
    u_is_draw = ControlledBool("u_is_draw", False)
    u_is_erase = ControlledBool("u_is_erase", False)
    u_prevmousepos = ControlledVec2("u_prevmousepos", vec2(0.0, 0.0))
    u_mousepos = ControlledVec2("u_mousepos", vec2(0.0, 0.0))

    def __init__(self, client):
        super(QRenderWidget, self).__init__()

        self.setMinimumSize(512, 512)
        self.setMaximumSize(512, 512)

        self.controlled_properties = [
            self.u_slider_value,
            self.u_is_draw,
            self.u_is_erase,
            self.u_prevmousepos,
            self.u_mousepos,
        ]

        client.value_change_signal.connect(self.set_value)

    def initializeGL(self):
        self.gl = mg.create_context()
        self.u_res = uvec2(512, 512)
        self.b_screen_draw = self.gl.buffer(reserve=512 * 512 * 4 * 4)
        self.b_screen_draw.bind_to_storage_buffer(1)

        self.compile()

        def on_modified(e):
            self.need_compile = True

        h = FileSystemEventHandler()
        h.on_modified = on_modified
        o = Observer()
        o.schedule(h, "./", True)
        o.start()

    def compile(self):
        self.need_compile = False

        try:
            CS = read("./gl/draw.cs")
            self.csdraw = self.gl.compute_shader(CS)

            VS, FS = read("./gl/quad.vs"), read("./gl/quad.fs")
            self.program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            self.vb = self.gl.buffer(read("./mesh/quad.vb", "rb"))
            self.ib = self.gl.buffer(read("./mesh/quad.ib", "rb"))
            content = [(self.vb, "2f", "in_pos")]
            self.vertex_array = self.gl.vertex_array(
                self.program, content, self.ib, skip_errors=True
            )

            self.pret = time.time() % 10000.0

            for cp in self.controlled_properties:
                cp.set(cp.get()[1])

            self.uniform("u_res", self.u_res)
            print("compiled")

        except Exception as e:
            print(e)

    def paintGL(self):
        if self.need_compile:
            self.compile()

        t = time.time() % 10000.0

        for cp in self.controlled_properties:
            if not cp.is_dirty:
                continue
            self.uniform(*cp.get())

        self.uniform("u_time", t)
        self.uniform("u_dtime", t - self.pret)

        self.pret = t

        self.csdraw.run(self.u_res.x // 8, self.u_res.y // 8)
        self.vertex_array.render()
        self.update()

    def uniform(self, uname, uvalue):
        programs = [self.program, self.csdraw]
        for p in programs:
            if uname not in p:
                continue

            if isinstance(uvalue, (int, float)):
                p[uname].value = uvalue
            else:
                p[uname].write(bytes(uvalue))

    @pyqtSlot(vec3)
    def set_value(self, value):
        self.u_slider_value.set(value)

    def mousePressEvent(self, e):
        self.u_mousepos.set(vec2(e.x(), e.y()))
        if e.button() == Qt.LeftButton:
            self.u_prevmousepos.set(self.u_mousepos.value)
            self.u_is_draw.set(True)
        elif e.button() == Qt.RightButton:
            self.u_prevmousepos.set(self.u_mousepos.value)
            self.u_is_erase.set(True)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.u_is_draw.set(False)
        elif e.button() == Qt.RightButton:
            self.u_is_erase.set(False)

    def mouseMoveEvent(self, e):
        self.u_prevmousepos.set(self.u_mousepos.value)
        self.u_mousepos.set(vec2(e.x(), e.y()))


class Client(QtWidgets.QMainWindow):
    value_change_signal = pyqtSignal(vec3)

    def __init__(self):
        super(Client, self).__init__()

        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Drawing and Raymarching")

        root = QtWidgets.QWidget()
        self.setCentralWidget(root)
        root_layout = QtWidgets.QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root.setLayout(root_layout)

        self.render_widget = QRenderWidget(self)
        root_layout.addWidget(self.render_widget)

        self.value_slider_x = QtWidgets.QSlider()
        self.value_slider_x.setOrientation(Qt.Horizontal)
        self.value_slider_x.valueChanged.connect(self.on_value_slider_changed)
        root_layout.addWidget(self.value_slider_x)

        self.value_slider_y = QtWidgets.QSlider()
        self.value_slider_y.setOrientation(Qt.Horizontal)
        self.value_slider_y.valueChanged.connect(self.on_value_slider_changed)
        root_layout.addWidget(self.value_slider_y)

        self.value_slider_z = QtWidgets.QSlider()
        self.value_slider_z.setOrientation(Qt.Horizontal)
        self.value_slider_z.valueChanged.connect(self.on_value_slider_changed)
        root_layout.addWidget(self.value_slider_z)

    def on_value_slider_changed(self, value):
        self.value_change_signal.emit(
            vec3(
                self.value_slider_x.value() / 100.0,
                self.value_slider_y.value() / 100.0,
                self.value_slider_z.value() / 100.0,
            )
        )


def main():
    app = QtWidgets.QApplication([])
    client = Client()
    client.show()
    app.exec()


if __name__ == "__main__":
    main()
