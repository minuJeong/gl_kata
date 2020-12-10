import glfw
import imgui
import numpy as np
from glm import vec4

from imgui_int import ModernGLGLFWRenderer


class Mesh(object):
    program = None
    vertices = None
    indices = None
    vertex_description = None
    vertex_array = None

    _is_dirty = True

    def read_shaders(self):
        raise NotImplemented

    def read_vertices(self):
        raise NotImplemented

    def compile_shaders(self):
        raise NotImplemented

    def render(self):
        if self.is_dirty():
            try:
                self.compile_shaders()
                print("compiled shaders")

            except Exception as e:
                print(e)

            finally:
                self.clear_dirty()
                return

        self.vertex_array.render()

    def uniform(self, key, value):
        if self.program is None:
            return

        if key not in self.program:
            return

        self.program[key] = value

    def is_dirty(self):
        return self._is_dirty

    def set_dirty(self):
        self._is_dirty = True

    def clear_dirty(self):
        self._is_dirty = False


class Quad(Mesh):
    def __init__(self, gl, window, vs_path="", fs_path=""):
        super().__init__()

        self.gl = gl

        self.vs_path, self.fs_path = vs_path, fs_path

        imgui.create_context()
        self.imgui = ModernGLGLFWRenderer(
            ctx=self.gl, display_size=(glfw.get_window_size(window))
        )
        self.imgui.wire_events(self.gl, window)

    def read_shaders(self):
        return open(self.vs_path).read(), open(self.fs_path).read()

    def read_vertices(self):
        self.vertices = np.array(
            [
                *vec4(-1.0, -1.0, 0.0, 1.0),
                *vec4(+1.0, -1.0, 0.0, 1.0),
                *vec4(-1.0, +1.0, 0.0, 1.0),
                *vec4(+1.0, +1.0, 0.0, 1.0),
            ],
            dtype=np.float32,
        )
        self.indices = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))
        self.vertex_description = [(self.gl.buffer(self.vertices), "4f", "in_pos")]

    def compile_shaders(self):
        self.read_vertices()
        vs, fs = self.read_shaders()
        self.program = self.gl.program(vertex_shader=vs, fragment_shader=fs)
        self.vertex_array = self.gl.vertex_array(
            self.program, self.vertex_description, self.indices
        )

    def render(self):
        super().render()

        imgui.new_frame()
        imgui.begin("debug")
        imgui.text(f"time {glfw.get_time():.2f}")
        imgui.end()
        imgui.render()
        self.imgui.render(imgui.get_draw_data())


if __name__ == "__main__":
    from main import main

    main()
