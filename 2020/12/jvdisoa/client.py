import glfw
import numpy as np
import moderngl as mg
import imageio as ii
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from mesh import Quad


class Client(object):
    def __init__(self, window):
        super().__init__()
        self.window = window

        self.gl = mg.create_context()
        self.meshes = [Quad(self.gl, window, "./gl/quad.vs", "./gl/quad.fs")]

        handler = FileSystemEventHandler()
        handler.on_modified = self.on_watch_gl_update
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

        self.writer = ii.get_writer("./capture.mp4", fps=60)
        self.color_buffer = self.gl.texture((512, 512), 4, dtype="f1")
        self.frame = self.gl.framebuffer([self.color_buffer])

    def on_watch_gl_update(self, e=None):
        for m in self.meshes:
            m.set_dirty()

    def read_shaders(self):
        for m in self.meshes:
            yield m.read_shaders()

    def compile_shaders(self):
        for m in self.meshes:
            m.compile_shaders()

    def uniform(self, key, value):
        for m in self.meshes:
            m.uniform(key, value)

    def render(self):
        self.gl.screen.use()
        for m in self.meshes:
            m.render()

        self.frame.use()
        for m in self.meshes:
            m.render()

        frame_img = np.frombuffer(self.color_buffer.read(), dtype=np.uint8).reshape((512, 512, 4))
        frame_img = frame_img[::-1]
        self.writer.append_data(frame_img)

    def update(self):
        self.uniform("u_time", glfw.get_time())
        self.render()

    def on_close(self):
        self.writer.close()


if __name__ == "__main__":
    from main import main

    main()
