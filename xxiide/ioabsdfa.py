"""
shader recompiler

author: minu jeong
"""


from threading import Thread
from threading import Event
from queue import Queue

import moderngl as mg
import numpy as np
import imageio as ii

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt


u_width, u_height = 512, 512


def read(path):
    with open(path, "r") as fp:
        return fp.read()


def set_uniform(p, n, v):
    if p and n in p:
        p[n].value = v


def serialize(data):
    data = np.frombuffer(data, dtype=np.float32)
    data = data.reshape((u_height, u_width, 4))
    data = data[:-1, :, :]
    data = np.multiply(data, 255.0)
    data = data.astype(np.uint8)
    return data


class ProgressRecorder(Thread):

    is_done = Event()
    queue = Queue()

    def __init__(self, path):
        super(ProgressRecorder, self).__init__()
        self.path = path

    def run(self):
        self.is_done.clear()

        writer = ii.get_writer(self.path)

        while True:
            if self.queue.empty():
                if self.is_done.is_set():
                    break
                continue

            data = self.queue.get()
            writer.append_data(serialize(data))

        writer.close()


class Handler(FileSystemEventHandler):
    def __init__(self, on_mod):
        super(Handler, self).__init__()
        self.on_modified = on_mod


def on_change(recorder=None):
    try:
        print("on_change!")

        gl = mg.create_standalone_context()
        cs = gl.compute_shader(read("./gl/compute.glsl"))

        set_uniform(cs, "u_width", u_width)
        set_uniform(cs, "u_height", u_height)

        data_0 = gl.buffer(reserve=u_width * u_height * 4 * 4)
        data_0.bind_to_storage_buffer(0)

        gx, gy = int(u_width / 8), int(u_height / 8)
        cs.run(gx, gy)

        data = data_0.read()

        if recorder:
            recorder.queue.put(data)

        ii.imwrite("output.png", serialize(data))

    except Exception as e:
        print("Exception while recompiling compute shader: ", e.__repr__())


def main():
    on_change()

    recorder = ProgressRecorder("output.mp4")
    recorder.start()

    file_mod_handler = Handler(lambda x: on_change(recorder))
    observer = Observer()
    observer.schedule(file_mod_handler, "./gl", recursive=True)
    observer.start()

    app = QtWidgets.QApplication([])
    stop_button = QtWidgets.QPushButton("Stop!")

    def on_stop():
        recorder.is_done.set()
        stop_button.close()
        observer.stop()
        app.quit()

    stop_button.setMinimumSize(220, 220)
    stop_button.clicked.connect(on_stop)
    stop_button.setWindowFlags(Qt.WindowStaysOnTopHint)
    stop_button.show()
    app.exec()

    recorder.join()
    observer.join()

    print("gracefully closing main thread")


if __name__ == "__main__":
    main()
