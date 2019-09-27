from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Pipe

import glfw
import moderngl as mg
import numpy as np
import imageio as ii

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Recorder(Process):
    def __init__(self, width, height, data_queue, done_flag):
        super(Recorder, self).__init__()
        self.width, self.height = width, height
        self.should_close = False
        self.data_queue = data_queue
        self.done_flag = done_flag

    def deserialize(self, data_bytes):
        data = np.frombuffer(data_bytes, dtype=np.float32)
        data = np.multiply(data, 255.0).astype(np.uint8)
        data = data.reshape((self.height, self.width, 3))
        return data

    def run(self):
        import sys
        writer = ii.get_writer("recording.mp4")

        i = 0
        while not self.done_flag:
            if self.data_queue.empty():
                continue

            data_bytes = self.data_queue.get()
            writer.append_data(self.deserialize(data_bytes))

            i += 1
            if i % 10 == 0:
                print(f"processing {i}th frame..")
                sys.stdout.flush()

        writer.close()

        print("multiprocess recorder: done!")
        sys.stdout.flush()


class Context(object):
    def __init__(self, width, height):
        super(Context, self).__init__()

        self.recorder = None

        self.GL = mg.create_context()

        self.width, self.height = width, height
        self.screenvbo = self.GL.buffer(reserve=4 * 4 * 4)
        self.screenibo = self.GL.buffer(reserve=6 * 4)
        self.screenvbo.bind_to_storage_buffer(0)
        self.screenibo.bind_to_storage_buffer(1)

        self.programs = []
        self.vertex_arrays = []

        self.recompile()

        def on_mod(e):
            self._should_recomile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_mod
        observer = Observer()
        observer.schedule(handler, "./gl")
        observer.start()

    def uniform(self, data):
        for p in self.programs:
            for n, v in data.items():
                if n in p:
                    p[n].value = v

    def read(self, path):
        with open(path, "r") as fp:
            content = fp.read()

        lines = []
        for line in content.splitlines():
            if line.startswith("#include "):
                external = self.read(line.split("#include ")[1])
                lines.append(external)

            else:
                lines.append(line)

        return "\n".join(lines)

    def recompile(self):
        self._should_recomile = False

        try:
            self.programs.clear()
            self.vertex_arrays.clear()

            screenmesh_builder = self.GL.compute_shader(
                self.read("./gl/screenmesh_builder.glsl")
            )
            self.programs.append(screenmesh_builder)
            screenmesh_builder.run(1)

            screen_program = self.GL.program(
                vertex_shader=self.read("./gl/vertex_shader.glsl"),
                fragment_shader=self.read("./gl/fragment_shader.glsl"),
            )
            self.programs.append(screen_program)

            screen_vertex_array = self.GL.vertex_array(
                screen_program, [(self.screenvbo, "4f", "in_pos")], self.screenibo
            )
            self.vertex_arrays.append(screen_vertex_array)
            print("recompiled")

        except Exception as e:
            print(e)

        self.uniform({"u_resolution": (self.width, self.height)})

    def render(self, t):
        if self._should_recomile:
            self.recompile()
            return

        self.uniform({"u_time": t})
        for vao in self.vertex_arrays:
            vao.render()

        pass

    def start_recording(self):
        pass

    def close_recording(self):
        pass


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    width, height = 800, 608
    window = glfw.create_window(width, height, "GLFW", None, None)
    glfw.make_context_current(window)

    context = Context(width, height)
    context.start_recording()

    while not glfw.window_should_close(window):
        context.render(glfw.get_time())

        glfw.poll_events()
        glfw.swap_buffers(window)

    context.close_recording()


if __name__ == "__main__":
    main()
