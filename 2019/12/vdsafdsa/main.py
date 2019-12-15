import glfw
import moderngl as mg
import numpy as np
from glm import *

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


WIDTH, HEIGHT = 1920 // 2, 1080 // 2


def read(path):
    with open(path, "r") as fp:
        return fp.read()


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window

        self.gl = mg.create_context()

        self.volume_res = ivec3(128, 128, 128)
        self.compute_group_res = self.volume_res / 8

        self.compile()

        # start shader code observer
        h = FileSystemEventHandler()
        h.on_modified = self.on_modified
        o = Observer()
        o.schedule(h, "./gl/", True)
        o.start()

    def on_modified(self, e):
        self.shader_should_compile = True

    def uniform(self, p, n, v):
        if n not in p:
            return

        if isinstance(v, (vec2, vec3, vec4)):
            p[n].write(bytes(v))
        elif isinstance(v, (ivec2, ivec3, ivec4)):
            p[n].write(bytes(v))
        elif isinstance(v, (uvec2, uvec3, uvec4)):
            p[n].write(bytes(v))
        elif isinstance(v, (mat2, mat3, mat4)):
            p[n].write(bytes(v))
        else:
            p[n].value = v

    def compile(self):
        self.shader_should_compile = False

        gl = self.gl

        try:
            self.cs_truchet = gl.compute_shader(read("./gl/truchet.compute"))
            self.p_render = gl.program(
                vertex_shader=read("./gl/pass.vert"),
                fragment_shader=read("./gl/render.frag"),
            )

            vbdata = (
                np.array([-1.0, -1.0, +1.0, -1.0, -1.0, +1.0, +1.0, +1.0])
                .astype(np.float32)
                .tobytes()
            )
            ibdata = np.array([0, 1, 2, 2, 1, 3]).astype(np.int32).tobytes()
            vb, ib = gl.buffer(vbdata), gl.buffer(ibdata)
            self.vao = gl.vertex_array(self.p_render, [(vb, "2f", "in_pos")], ib, skip_errors=True)

            vsize = self.volume_res.x * self.volume_res.y * self.volume_res.z
            vsize *= 4 * 4
            self.truchet_volume = gl.buffer(reserve=vsize)
            self.truchet_volume.bind_to_storage_buffer(14)

            self.uniform(self.cs_truchet, "u_volume_res", self.volume_res)
            self.uniform(self.p_render, "u_volume_res", self.volume_res)

            print("compiled")

        except Exception as e:
            print(e)

    def update(self):
        if self.shader_should_compile:
            self.compile()

        t = glfw.get_time()
        self.uniform(self.cs_truchet, "u_time", t)
        self.uniform(self.p_render, "u_time", t)

        self.cs_truchet.run(*self.compute_group_res)
        self.vao.render()


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(512, 512, "hello", None, None)
    glfw.make_context_current(window)
    client = Client(window)
    while not glfw.window_should_close(window):
        client.update()
        glfw.poll_events()
        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
