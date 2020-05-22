import time
import struct

import numpy as np
import moderngl as mg
from psd_tools import PSDImage
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt


class Window(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setMinimumSize(900, 900)
        self.setMaximumSize(900, 900)

    def initializeGL(self):
        self.gl = mg.create_context(require=460)

        self.compile_shaders()
        self.load_textures()

        def on_modified(event):
            self._need_compile = True

        def on_modified_textures(event):
            self._need_reload_texture = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_modified
        handler_texture = FileSystemEventHandler()
        handler_texture.on_modified = on_modified_textures
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.schedule(handler_texture, "./resource", True)
        observer.start()

    def compile_shaders(self):
        self._need_compile = False

        try:
            vertex_shader_source = open("./gl/quad.vs").read()
            fragment_shader_source = open("./gl/quad.fs").read()
            self.program = self.gl.program(
                vertex_shader=vertex_shader_source,
                fragment_shader=fragment_shader_source
            )

            vertex_bytes = struct.pack(
                "16f",
                -1.0, -1.0, 0.0, 1.0,
                +1.0, -1.0, 0.0, 1.0,
                -1.0, +1.0, 0.0, 1.0,
                +1.0, +1.0, 0.0, 1.0
            )
            index_bytes = struct.pack("6i", 0, 1, 2, 2, 1, 3)
            vertex = [(self.gl.buffer(vertex_bytes), "4f", "in_position")]
            index = self.gl.buffer(index_bytes)
            self.vertex_array = self.gl.vertex_array(self.program, vertex, index)

            print("compiled")

        except Exception as e:
            print(e)

    def load_textures(self):
        try:
            psd_img = PSDImage.open("./resource/test.psd")
            img = psd_img.compose()
            img = np.array(img)
            self.texture = self.gl.texture((img.shape[1], img.shape[0]), img.shape[2], img)
            self._need_reload_texture = False

        except Exception as e:
            print(e)

    def paintGL(self):
        if self._need_compile:
            self.compile_shaders()

        if self._need_reload_texture:
            self.load_textures()

        if "u_time" in self.program:
            self.program["u_time"] = time.time() % 1000000

        self.texture.use(0)
        self.vertex_array.render()
        self.update()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Window()
    window.show()
    app.exec_()
