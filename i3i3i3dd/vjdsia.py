import numpy as np
import moderngl as mg
import glfw
import glm

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

    compute_shaders = {}
    programs = []
    vaos = []

    def __init__(self, gl, width, height, volume_res):
        super(Context, self).__init__()
        self.gl = gl
        self._vaos = []

        self.u_res = glm.ivec2(width, height)
        self.u_vsize = glm.ivec3(volume_res)
        self.gx, self.gy, self.gz = (
            int(self.u_vsize.x / 4),
            int(self.u_vsize.y / 4),
            int(self.u_vsize.z / 4),
        )

    def on_src_modified(self, e=None):
        self.should_recompile = True

    def recompile(self):
        self.should_recompile = False

        try:
            gl = self.gl

            self.cs_0 = gl.compute_shader(read("./gl/scene.cs"))
            self.compute_shaders[self.gx, self.gy, self.gz] = self.cs_0

            content = [(self.vbo, "2f", "in_pos")]
            program = gl.program(
                vertex_shader=read("./gl/default_vs.glsl"),
                fragment_shader=read("./gl/visualize_volume_fs.glsl"),
            )

            self.programs.append(program)
            self.vaos.append(gl.vertex_array(program, content, self.ibo))

            print("recompiled!")

        except Exception as e:
            print(e)

    def init(self):
        gl = self.gl

        WHD = glm.ivec3(self.u_vsize)
        self.volume_0 = gl.buffer(reserve=WHD.x * WHD.y * WHD.z * 4)

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

    def _uniform(self, p, uniform):
        for n, v in {}.items():
            if n not in p:
                continue

            p[n].value = v

    def init_uniforms(self):
        init_uniform = {
            "u_res": self.u_res,
            "u_vsize": self.u_vsize,
        }
        for cs in self.compute_shaders.values():
            self._uniform(cs, init_uniform)

        for program in self.programs:
            self._uniform(program, init_uniform)

    def frame_uniforms(self):
        frame_uniform = {"u_time": glfw.get_time()}
        for cs in self.compute_shaders.values():
            self._uniform(cs, frame_uniform)

        for program in self.programs:
            self._uniform(program, frame_uniform)

    def render(self):
        for xyz, cs in self.compute_shaders.items():
            cs.run(xyz[0], xyz[1], xyz[2])

        for vao in self.vaos:
            vao.render()

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
    ctx.init_uniforms()

    MINIMUM_TICK = 1.0 / 24.0
    t = glfw.get_time()
    while not glfw.window_should_close(window):
        ctx.poll_recompile()
        ctx.frame_uniforms()
        ctx.render()

        glfw.swap_buffers(window)
        glfw.poll_events()

        while glfw.get_time() - t < MINIMUM_TICK:
            pass

        t = glfw.get_time()


if __name__ == "__main__":
    main()
