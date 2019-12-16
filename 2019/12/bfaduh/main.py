import time

from glm import *
import moderngl as mg
from PyQt5 import QtWidgets
from PyQt5.Qt import Qt
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def read(path, mode):
    with open(path, mode) as fp:
        return fp.read()


class UValue(object):
    subscriptions = []

    @staticmethod
    def update():
        for uv in UValue.subscriptions:
            uv._update()

    def __init__(self, programs, uname, uvalue):
        super(UValue, self).__init__()
        self.programs = programs
        self.uname, self.uvalue = uname, uvalue
        self.is_dirty = True

        UValue.subscriptions.append(self)

    def set(self, value):
        self.is_dirty = True
        self.uvalue = value

    def _update(self):
        if not self.is_dirty:
            return

        for program in self.programs:
            if self.uname not in program:
                continue

            if isinstance(self.uvalue, (float, int)):
                program[self.uname].value = self.uvalue
            else:
                program[self.uname].write(bytes(self.uvalue))


class QRenderWidget(QtWidgets.QOpenGLWidget):
    def initializeGL(self):
        self.width, self.height = 1920, 1080
        self.setMinimumSize(self.width, self.height)
        self.setMaximumSize(self.width, self.height)

        self.gl = mg.create_context()

        self.u_camerapos = UValue([], "", vec3(0.0, 2.0, 5.0))
        self.compile()

        def on_modified(e):
            self.should_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_modified

        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

    def compile(self):
        self.should_compile = False

        try:
            VS, FS = read("./gl/quad.vs", "r"), read("./gl/quad.fs", "r")
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            VERTICES, INDICES = read("./mesh/quad.vb", "rb"), read("./mesh/quad.ib", "rb")
            stride, attrnames = "4f 4f", ["in_pos", "in_texcoord0"]
            vertices = [(self.gl.buffer(VERTICES), stride, *attrnames)]
            indices = self.gl.buffer(INDICES)
            self.vao = self.gl.vertex_array(program, vertices, indices, skip_errors=True)

            self.u_time = UValue([program], "u_time", 0.0)
            self.u_camerapos = UValue([program], "u_camerapos", self.u_camerapos.uvalue)
            self.u_aspect = UValue([program], "u_aspect", self.width / self.height)

            self.mousepos = vec2(0.0)

            print("compiled")

        except Exception as e:
            print(e)

    def paintGL(self):
        if self.should_compile:
            self.compile()

        t = time.time() % 10000.0
        self.u_time.set(t)

        UValue.update()
        self.vao.render()
        self.update()

    def mousePressEvent(self, e):
        self.mousepos = vec2(e.x(), e.y())

    def mouseReleaseEvent(self, e):
        pass

    def mouseMoveEvent(self, e):
        mp = vec2(e.x(), e.y())
        dx, dy = mp - self.mousepos
        self.mousepos = mp

        rot = quat(vec3(0.0, -dx, 0.0) * 0.005)
        ppos = self.u_camerapos.uvalue
        ppos = ppos * rot
        self.u_camerapos.set(ppos)


class Client(QtWidgets.QMainWindow):

    def __init__(self):
        super(Client, self).__init__()

        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        root = QtWidgets.QWidget()
        self.setCentralWidget(root)

        rootlayout = QtWidgets.QVBoxLayout()
        rootlayout.setContentsMargins(0, 0, 0, 0)
        root.setLayout(rootlayout)

        renderwidget = QRenderWidget()
        rootlayout.addWidget(renderwidget)


def main():
    app = QtWidgets.QApplication([])
    client = Client()
    client.show()
    app.exec()


if __name__ == "__main__":
    main()
