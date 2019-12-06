import numpy as np
import moderngl as mg
import imageio as ii
import glfw
from glm import *

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def readshader(path):
    with open(path, "r") as fp:
        return fp.read()


def readbytes(path):
    with open(path, "rb") as fp:
        return fp.read()


class Mesh(object):
    def __init__(self, gl, vbib, vsfs):
        self.program = gl.program(
            vertex_shader=readshader(vsfs[0]), fragment_shader=readshader(vsfs[1])
        )

        self.vb = readbytes(vbib[0])
        self.ib = readbytes(vbib[1])

    def uniform(self, n, v):
        if n not in self.program:
            return

        u = self.program[n]
        if isinstance(v, (vec3, vec4, mat4)):
            u.write(bytes(v))
        else:
            u.value = v


class ScreenMesh(Mesh):
    def __init__(self, gl, vbib, vsfs):
        super(ScreenMesh, self).__init__(gl, vbib, vsfs)
        vb_content = [(gl.buffer(self.vb), "4f 2f", "in_pos", "in_texcoord",)]
        self.vao = gl.vertex_array(
            self.program, vb_content, gl.buffer(self.ib), skip_errors=True,
        )
        self.render = self.vao.render


class Scene(object):
    def on_modified(self, e):
        self.should_compile = True

    def on_key(self, window, scancode, keycode, action, mods):
        if action == glfw.RELEASE:
            if scancode == glfw.KEY_SPACE:
                self.render_to_texture()

    def __init__(self, window, width, height):
        super(Scene, self).__init__()

        self.window = window
        self.width, self.height = width, height

        print("initializing gpu..")
        self.gl = mg.create_context()

        self.compile()

        h = FileSystemEventHandler()
        h.on_modified = self.on_modified
        o = Observer()
        o.schedule(h, "./gl/", True)
        o.start()

        glfw.set_key_callback(window, self.on_key)

    def compile(self):
        self.should_compile = False
        self.meshes = []
        try:
            self.camera_pos = vec3(-5.0, 5.0, -5.0)
            self.meshes.append(
                ScreenMesh(
                    self.gl,
                    ("./mesh/screen_mesh.vb", "./mesh/screen_mesh.ib"),
                    ("./gl/vs_screen.glsl", "./gl/fs_screen.glsl"),
                )
            )

            self.uniform("u_aspect", self.width / self.height)

            img = ii.imread("./noise_cache.png")
            w, h, c = 0, 0, 0
            if len(img.shape) == 2:
                h, w = img.shape
                c = 1
            else:
                h, w, c = img.shape

            tex = self.gl.texture((w, h), c, data=img.tobytes())
            tex.use(0)
            self.uniform("u_noisecache", 0)
            print("compiled Draw")

        except Exception as e:
            print(e)

        self.prev_t = glfw.get_time()
        self.elapsed_frames = 0

    def uniform(self, n, v):
        for mesh in self.meshes:
            mesh.uniform(n, v)

    def _render(self):
        for mesh in self.meshes:
            mesh.render()

    def render(self):
        self.gl.clear()
        if self.should_compile:
            self.compile()
            return

        self.elapsed_frames += 1
        t = glfw.get_time()

        self.uniform("u_time", t)
        self.uniform("u_camerapos", self.camera_pos)

        self.gl.screen.use()
        self._render()

        if not self.elapsed_frames % 100:
            dt = t - self.prev_t
            print(f"framerate: {1.0 / dt:.2f}")

        self.prev_t = t

    def render_to_texture(self):
        print("rendering to texture..")

        w, h = self.width, self.height
        tex = self.gl.texture((w, h), 1, dtype="f1")
        frame = self.gl.framebuffer((tex))
        frame.use()
        self._render()

        tex_data = tex.read()
        img = np.frombuffer(tex_data, dtype=np.ubyte).reshape((h, w, 1))
        ii.imwrite("./noise_cache.png", img)

        tex = self.gl.texture((w, h), 1, data=tex_data)
        tex.use(0)
        self.uniform("u_noisecache", 0)


def main():
    width, height = 2048, 1024
    title = "CHAOS REALM BOUNDARY"

    print("initializing glfw..")

    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(width, height, title, None, None)
    # glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    glfw.make_context_current(window)
    scene = Scene(window, width, height)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        scene.render()
        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
