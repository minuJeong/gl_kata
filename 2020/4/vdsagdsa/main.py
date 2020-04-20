import time

import moderngl as mg
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from psd_tools import PSDImage


class Render(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(Render, self).__init__()

        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.setMinimumSize(800, 800)
        self.setMaximumSize(800, 800)

        self.width = self.size().width()
        self.height = self.size().height()

    def initializeGL(self):
        self.gl = mg.create_context()
        self.vertices = self.gl.buffer(
            np.array(
                [
                    (-1.0, -1.0, 0.0, 1.0),
                    (+1.0, -1.0, 0.0, 1.0),
                    (-1.0, +1.0, 0.0, 1.0),
                    (+1.0, +1.0, 0.0, 1.0),
                ],
                dtype=np.float32,
            )
        )
        self.indices = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))

        self.reload_textures()
        self.recompile_shaders()

        handler_gl = FileSystemEventHandler()
        handler_gl.on_modified = self.on_gl_src_modified
        handler_resources = FileSystemEventHandler()
        handler_resources.on_modified = self.on_resources_modified
        oberver = Observer()
        oberver.schedule(handler_gl, "./gl", True)
        oberver.schedule(handler_resources, "./resources", True)
        oberver.start()

    def recompile_shaders(self):
        self._need_recompile = False

        try:
            VS = open("./gl/quad.vs").read()
            FS = open("./gl/quad.fs").read()
            self.program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            if "u_resolution" in self.program:
                self.program["u_resolution"] = (self.width, self.height)
            self.quad = self.gl.vertex_array(
                self.program, [(self.vertices, "4f", "in_pos")], self.indices
            )
            print("shaders recompiled.")

        except Exception as e:
            print(e)

    def reload_textures(self):
        self._need_reload_textures = False

        try:
            self.textures = []
            psd = PSDImage.open("./resources/test_resource.psd")
            for layer in psd:
                img = np.array(layer.compose(bbox=psd.bbox))
                texture = self.gl.texture((img.shape[1], img.shape[0]), img.shape[2], img)
                self.textures.append(texture)

            print("textures reloaded")

        except Exception as e:
            print(e)

    def paintGL(self):
        if self._need_recompile:
            self.recompile_shaders()

        if self._need_reload_textures:
            self.reload_textures()

        if "u_time" in self.program:
            self.program["u_time"] = time.time() % 100000.0

        for i, texture in enumerate(self.textures):
            texture.use(i)
        self.quad.render()
        self.update()

    def on_gl_src_modified(self, e):
        self._need_recompile = True

    def on_resources_modified(self, e):
        self._need_reload_textures = True


def entry():
    app = QtWidgets.QApplication([])
    render = Render()
    render.show()
    app.exec_()


if __name__ == "__main__":
    entry()
