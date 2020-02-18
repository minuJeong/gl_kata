import time

from glm import *
import moderngl as mg
from PyQt5 import QtWidgets
from PyQt5.Qt import Qt
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class QRenderWidget(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(QRenderWidget, self).__init__()
        self.setMinimumSize(1024, 1024)

    def uniform(self, uname, uvalue):
        if uname not in self.program:
            return

        try:
            self.program[uname].value = uvalue
        except:
            self.program[uname].write(bytes(uvalue))

    def initializeGL(self):
        self.gl = mg.create_context()
        self.compile()

        def onmod(e):
            self.need_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = onmod
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

    def compile(self):
        self.need_compile = False

        try:
            VS = open("./gl/vs.glsl", "r").read()
            FS = open("./gl/fs.glsl", "r").read()
            self.program = self.gl.program(vertex_shader=VS, fragment_shader=FS)

            vb = self.gl.buffer(open("./mesh/Box001.vbo", "rb").read())
            ib = self.gl.buffer(open("./mesh/Box001.ibo", "rb").read())
            self.vao = self.gl.vertex_array(
                self.program,
                [(vb, "4f 4f", "in_pos", "in_normal")],
                ib,
                skip_errors=True,
            )

            print("compiled")

        except Exception as e:
            print(e)

    def paintGL(self):
        if self.need_compile:
            self.compile()
            self.update()
            return

        t = time.time() % 10000.0
        campos = vec3(80.0)
        campos.x = cos(t) * 220.0
        campos.z = sin(t) * 220.0
        V = lookAt(campos, vec3(0.0, 10.0, 0.0), vec3(0.0, 1.0, 0.0))
        P = perspective(radians(45.0), 1.0, 0.02, 10000.0)
        u_MVP = P * V
        self.uniform("u_MVP", u_MVP)
        self.uniform("u_time", t)

        self.gl.enable(mg.DEPTH_TEST)
        self.vao.render()
        self.update()


class Client(QtWidgets.QMainWindow):
    def __init__(self):
        super(Client, self).__init__()

        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        root = QtWidgets.QWidget()
        root_layout = QtWidgets.QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root.setLayout(root_layout)
        self.setCentralWidget(root)

        self.render_widget = QRenderWidget()
        root_layout.addWidget(self.render_widget)


def main():
    app = QtWidgets.QApplication([])
    client = Client()
    client.show()
    app.exec_()


if __name__ == "__main__":
    main()
