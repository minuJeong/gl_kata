
import os
from itertools import product
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import moderngl as mg
import numpy as np

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt


class WatchdogWaiter(QThread):

    on_finished = pyqtSignal()

    def __init__(self):
        super(WatchdogWaiter, self).__init__()

    def run(self):
        class Handler(FileSystemEventHandler):
            def __init__(self, callback):
                super(Handler, self).__init__()
                self.callback = callback

            def on_modified(self, e):
                self.callback()

        handler = Handler(lambda: self.on_finished.emit())

        observer = Observer()
        observer.schedule(handler, "./gl", recursive=True)
        observer.start()
        observer.join()


class DebugRenderer(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(DebugRenderer, self).__init__()

        self.u_width, self.u_height = 128, 128
        self.u_size_hor, self.u_size_ver = 8, 8
        self.gx, self.gy = (
            int(self.u_width / self.u_size_hor),
            int(self.u_height / self.u_size_ver),
        )

        self.buffer_size = self.u_width * self.u_height * 4 * 4

        self.setMinimumSize(self.u_width, self.u_height)
        self.setMaximumSize(self.u_width, self.u_height)
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.WindowCloseButtonHint |
            Qt.WindowTransparentForInput
        )
        self.setWindowTitle("Debug Renderer")

    def read(self, path):
        """ gracefully read file contents at path """

        if not os.path.isfile(path):
            return ""

        try:
            with open(path, "r") as fp:
                return fp.read()

        except:
            return ""

    def uniforms(self, programs, names, values):
        """
        foreach p in programs -> p[names[i]].value = values[i]
        """

        for program, (n, v) in product(programs, zip(names, values)):
            if n in program:
                program[n].value = v

    def recompile_kernel(self):
        try:
            self.cs = self.gl.compute_shader(self.read("./gl/compute.glsl"))

            self.program = self.gl.program(
                vertex_shader=self.read("./gl/debug_vert.glsl"),
                fragment_shader=self.read("./gl/debug_frag.glsl"),
            )

            vbo = [-1.0, -1.0, -1.0, +1.0, +1.0, -1.0, +1.0, +1.0]
            vbo = np.array(vbo).astype(np.float32).tobytes()
            vbo = self.gl.buffer(vbo)
            content = [(vbo, "2f", "in_pos")]

            ibo = [0, 1, 2, 2, 1, 3]
            ibo = np.array(ibo).astype(np.int32).tobytes()
            ibo = self.gl.buffer(ibo)

            self.vao = self.gl.vertex_array(self.program, content, ibo)
            self.uniforms(
                [self.cs, self.program],
                ["u_width", "u_height"],
                [self.u_width, self.u_height],
            )

            print("Kernel recompiled")

        except Exception as e:
            print(e)

    def initializeGL(self):
        """
        called once at start
        """

        self.gl = mg.create_context()
        self.cs_buffer_0 = self.gl.buffer(reserve=self.buffer_size)
        self.cs_buffer_1 = self.gl.buffer(reserve=self.buffer_size)

        self.u_time = 0.0

        self.recompile_kernel()

        self.waiter = WatchdogWaiter()
        self.waiter.on_finished.connect(lambda: self.recompile_kernel())
        self.waiter.start()

    def paintGL(self):
        """
        called every frame
        """

        self.uniforms([self.cs, self.program], ["u_time"], [time.time() % 1000.0])

        self.cs_buffer_0.bind_to_storage_buffer(0)
        self.cs_buffer_1.bind_to_storage_buffer(1)

        self.cs.run(self.gx, self.gy)
        self.vao.render()
        self.update()


def main():
    app = QtWidgets.QApplication([])

    renderer = DebugRenderer()
    renderer.show()

    app.exec()


if __name__ == "__main__":
    main()
