import time

import numpy as np
import moderngl as mg
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Handler(FileSystemEventHandler):

    def __init__(self, callback):
        super(Handler, self).__init__()
        self.callback = callback

    def on_modified(self, e):
        self.callback()


class Watcher(QtCore.QThread):

    on_modified = QtCore.pyqtSignal()

    def __init__(self):
        super(Watcher, self).__init__()

    def run(self):
        observer = Observer()
        handler = Handler(lambda: self.on_modified.emit())
        observer.schedule(handler, "./gl/")
        observer.start()
        observer.join()


class Renderer(QtWidgets.QOpenGLWidget):

    def __init__(self):
        super(Renderer, self).__init__()
        u_width, u_height = 500, 500

        self.setMinimumSize(u_width, u_height)
        self.setMaximumSize(u_width, u_height)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

    def read(self, path):
        with open(path, 'r') as fp:
            return fp.read()

    def recompile_program(self):

        new_vao = None
        try:
            self.program = self.gl.program(
                vertex_shader=self.read("./gl/vs.glsl"),
                fragment_shader=self.read("./gl/fs.glsl")
            )

            new_vao = self.gl.vertex_array(self.program, [(self.vbo, "2f", "in_pos")], self.ibo)

            self.u_time = None
            if "u_time" in self.program:
                self.u_time = self.program["u_time"]

        except Exception as e:
            print(e)
            return

        if new_vao:
            self.vao = new_vao
        print("Recompiled Program!")

    def initializeGL(self):
        self.gl = mg.create_context()

        self.vbo = [-1.0, -1.0, +1.0, -1.0, -1.0, +1.0, +1.0, +1.0]
        self.vbo = np.array(self.vbo).astype(np.float32).tobytes()
        self.vbo = self.gl.buffer(self.vbo)
        self.ibo = [0, 1, 2, 2, 1, 3]
        self.ibo = np.array(self.ibo).astype(np.int32).tobytes()
        self.ibo = self.gl.buffer(self.ibo)

        self.recompile_program()

        self.watcher = Watcher()
        self.watcher.on_modified.connect(self.recompile_program)
        self.watcher.start()

    def paintGL(self):
        if self.u_time:
            self.u_time.value = time.time() % 1000.0
        self.vao.render()
        self.update()


def main():
    app = QtWidgets.QApplication([])
    renderer = Renderer()
    renderer.show()
    app.exec()


if __name__ == "__main__":
    main()
