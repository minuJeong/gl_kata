import numpy as np
import moderngl as mg
import glfw

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


width, height = 400, 400
volume_res = 48, 48, 48
title = "Hello GLFW"


def read(path):
    with open(path, "r") as fp:
        return fp.read()


class Context(object):
    gl = None
    should_recompile = False

    programs = []
    vaos = []

    def __init__(self, gl, width, height, volume_res):
        super(Context, self).__init__()
        self.gl = gl
        self._vaos = []

        self.u_width, self.u_height = width, height
        self.u_vsize = volume_res
        self.gx, self.gy, self.gz = (
            int(volume_res[0] / 4),
            int(volume_res[1] / 4),
            int(volume_res[2] / 4),
        )

    def on_src_modified(self, e=None):
        self.should_recompile = True

    def recompile(self):
        self.should_recompile = False

        try:
            gl = self.gl

            self.cs_0 = gl.compute_shader(read("./gl/scene.cs"))

            content = [(self.vbo, "2f", "in_pos")]
            program = gl.program(
                vertex_shader=read("./gl/default_vs.glsl"),
                fragment_shader=read("./gl/visualize_volume_fs.glsl"),
            )
            self.vaos.append(gl.vertex_array(program, content, self.ibo))

            print("recompiled!")

        except Exception as e:
            print(e)

    def init(self):
        gl = self.gl
        self.vbo = gl.buffer(
            np.array([-1.0, -1.0, -1.0, +1.0, +1.0, -1.0, +1.0, +1.0])
            .astype(np.float32)
            .tobytes()
        )
        self.ibo = gl.buffer(np.array([0, 1, 2, 2, 1, 3]).astype(np.int32).tobytes())

        self.recompile()

        recompile_handler = FileSystemEventHandler()
        recompile_handler.on_modified = self.on_src_modified
        self.src_observer = Observer()
        self.src_observer.schedule(recompile_handler, "./gl")
        self.src_observer.start()

    def render(self):
        self.cs_0.run(self.gx, self.gy, self.gz)
        list(map(lambda vao: vao.render(), self.vaos))

    def poll_recompile(self):
        if not self.should_recompile:
            return

        self.recompile()


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(width, height, title, None, None)
    glfw.make_context_current(window)

    ctx = Context(mg.create_context(), width, height, volume_res)
    ctx.init()

    MINIMUM_TICK = 1.0 / 24.0
    t = glfw.get_time()
    while not glfw.window_should_close(window):

        ctx.render()
        ctx.poll_recompile()

        glfw.swap_buffers(window)
        glfw.poll_events()

        while glfw.get_time() - t < MINIMUM_TICK:
            pass

        t = glfw.get_time()


if __name__ == "__main__":
    main()
