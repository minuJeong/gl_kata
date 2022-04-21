import time

import numpy as np
import moderngl as mg
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class WatchdogHandler(FileSystemEventHandler):
    def __init__(self, client):
        super().__init__()
        self.client = client

    def on_modified(self, e):
        self.client.should_compile = True


class RenderClient(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super().__init__()

    def initializeGL(self):
        self.gl = mg.create_context()

        self.should_compile = False

        self.vb = self.gl.buffer(
            np.array(
                [
                    *vec4(-1.0, -1.0, 0.0, 1.0),
                    *vec4(+1.0, -1.0, 0.0, 1.0),
                    *vec4(-1.0, +1.0, 0.0, 1.0),
                    *vec4(+1.0, +1.0, 0.0, 1.0),
                ],
                dtype=np.float32,
            )
        )
        self.ib = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))

        self.compile_shader()

        self.observer = Observer()
        self.observer.schedule(WatchdogHandler(self), "./gl/", True)
        self.observer.start()

    def compile_shader(self):
        self.program = self.gl.program(
            vertex_shader=open("./gl/quad.vs").read(),
            fragment_shader=open("./gl/quad.fs").read(),
        )

        self.quad = self.gl.vertex_array(
            self.program, [(self.vb, "4f", "in_pos")], self.ib
        )

        w, h = self.width(), self.height()

        if "u_resolution" in self.program:
            self.program["u_resolution"] = (*vec2(w, h),)

    def paintGL(self):
        if self.should_compile:
            self.should_compile = False
            try:
                self.compile_shader()
                print("compiled shaders")

            except Exception as e:
                print(e)

        if "u_time" in self.program:
            self.program["u_time"] = time.time() % 1000.0

        self.quad.render()
        self.update()

    def resizeEvent(self, e):
        if hasattr(self, "program") and "u_resolution" in self.program:
            self.compile_shader()


class Client(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.root = QtWidgets.QWidget()
        self.setCentralWidget(self.root)

        vbox_layout = QtWidgets.QVBoxLayout()
        self.root.setLayout(vbox_layout)

        self.render_client = RenderClient()
        vbox_layout.addWidget(self.render_client)

        button = QtWidgets.QPushButton("Hello")
        vbox_layout.addWidget(button)


def main():
    app = QtWidgets.QApplication([])

    client = Client()
    client.setWindowFlags(Qt.WindowStaysOnTopHint)
    client.show()

    app.exec()


if __name__ == "__main__":
    main()
