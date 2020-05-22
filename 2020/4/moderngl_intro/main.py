import struct

import numpy as np
import moderngl as mg
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from psd_tools import PSDImage


class Render(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(Render, self).__init__()
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.setMinimumSize(1024, 1024)
        self.setMaximumSize(1024, 1024)

    def initializeGL(self):
        self.gl = mg.create_context(require=460)

        self.compile()
        self.load_textures()

        def on_modified(e):
            self.need_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_modified
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

    def compile(self):
        self.need_compile = False

        try:
            VS, FS = open("./gl/quad.vs").read(), open("./gl/quad.fs").read()
            program = self.gl.program(
                vertex_shader=VS,
                fragment_shader=FS
            )

            width, height = self.size().width(), self.size().height()
            if "u_resolution" in program:
                program["u_resolution"] = (width, height)

            vertices_binary_data = struct.pack(
                "16f",
                -1.0, -1.0, 0.0, 1.0,
                +1.0, -1.0, 0.0, 1.0,
                -1.0, +1.0, 0.0, 1.0,
                +1.0, +1.0, 0.0, 1.0)
            indices_binary_data = struct.pack("6i", 0, 1, 2, 2, 1, 3)
            vertices_data = [(self.gl.buffer(vertices_binary_data), "4f", "in_position")]
            indices_data = self.gl.buffer(indices_binary_data)
            self.vertex_array = self.gl.vertex_array(program, vertices_data, indices_data)

            print("compiled")

        except Exception as e:
            print(e)

    def load_textures(self):
        psd_img = PSDImage.open("./resource/test.psd")
        img = np.array(psd_img.compose())

        self.texture = self.gl.texture((img.shape[1], img.shape[0]), img.shape[2], img)

    def paintGL(self):
        if self.need_compile:
            self.compile()

        self.texture.use(0)
        self.vertex_array.render()
        self.update()


app = QtWidgets.QApplication([])
render = Render()
render.show()
app.exec_()
