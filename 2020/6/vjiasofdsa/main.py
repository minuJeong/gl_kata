import imgui
import glfw
import moderngl as mg
import numpy as np
import imageio as ii
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from imgui_integration import ModernGLGLFWRenderer


WIDTH, HEIGHT = 800, 600


class Client(object):
    def __init__(self, window):
        super().__init__()

        self.window = window
        self.width, self.height = WIDTH, HEIGHT

        self.gl = mg.create_context()

        self.rotation = vec2(0.0, 0.0)
        self.u_campos = vec3(-2.0, 2.0, 5.0)

        self._prevpos = ivec2(0, 0)
        self._isdrag = False

        self.compile_shaders()

        def _on_mod(e):
            self.should_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = _on_mod
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.schedule(handler, "./tex", True)
        observer.start()

        imgui.create_context()
        self.imgui = ModernGLGLFWRenderer(ctx=self.gl, display_size=(WIDTH, HEIGHT))
        self.imgui.wire_events(self.gl, window)
        self.imgui.on_mouse_button = self.on_mouse_button
        self.imgui.on_cursor_pos = self.on_cursor_pos

    def on_resize(self, window, width, height):
        self.width, self.height = width, height
        self.gl.viewport = (0, 0, self.width, self.height)
        self.uniform("u_resolution", (self.width, self.height))

    def on_mouse_button(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT and mods == glfw.MOD_ALT:
            if action == glfw.PRESS:
                self._isdrag = True
                self._prevpos = ivec2(*glfw.get_cursor_pos(window))
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE)
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
            elif action == glfw.RELEASE:
                self._isdrag = False
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.FALSE)
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def on_cursor_pos(self, window, x, y):
        if not self._isdrag:
            return

        pos = ivec2(x, y)
        delt = pos - self._prevpos
        self._prevpos = pos

        up = vec3(0.0, 1.0, 0.0)
        self.u_campos = (
            rotate(mat4(1.0), delt.x * 0.01, up) * vec4(self.u_campos, 1.0)
        ).xyz
        right = cross(normalize(self.u_campos), up)
        self.u_campos = (
            rotate(mat4(1.0), delt.y * 0.01, right) * vec4(self.u_campos, 1.0)
        ).xyz
        self.uniform("u_campos", self.u_campos)

    def compile_shaders(self):
        self.should_compile = False

        try:
            VS, FS = open("./gl/quad.vs").read(), open("./gl/quad.fs").read()
            p = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            v = self.gl.buffer(
                np.array(
                    [
                        [-1.0, -1.0, 0.0, 1.0],
                        [-1.0, +1.0, 0.0, 1.0],
                        [+1.0, -1.0, 0.0, 1.0],
                        [+1.0, +1.0, 0.0, 1.0],
                    ],
                    dtype=np.float32,
                )
            )
            i = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))
            self.quad = self.gl.vertex_array(p, [(v, "4f", "in_pos")], i)

            tex_data = ii.imread("./tex/test_tex.png")
            self.tex = self.gl.texture((tex_data.shape[1], tex_data.shape[0]), tex_data.shape[2], tex_data)
            self.uniform("u_tex", 0)

            self.uniform("u_resolution", (self.width, self.height))
            print("compiled shaders")

        except Exception as e:
            print(e)

    def render(self):
        self.tex.use(0)
        self.quad.render()

    def render_ui(self):
        imgui.new_frame()
        imgui.begin("camera")

        is_change_y, self.u_campos.y = imgui.slider_float(
            "y", self.u_campos.y, -3.14159 * 4.0, 3.14159 * 4.0
        )
        if is_change_y:
            self.uniform("u_campos", self.u_campos)

        imgui.end()
        imgui.render()
        self.imgui.render(imgui.get_draw_data())

    def uniform(self, uname, uvalue):
        p = self.quad.program
        if uname not in p:
            return

        if isinstance(uvalue, (float, int, tuple)):
            p[uname] = uvalue
        elif isinstance(uvalue, list):
            p[uname] = tuple(uvalue)
        elif isinstance(uvalue, (vec2, vec3, vec4)):
            p[uname] = (*uvalue,)
        else:
            print(f"unrecognized type: {type(uvalue), uname, uvalue}")

    def update(self):
        if self.should_compile:
            self.compile_shaders()
            return

        self.uniform("u_time", glfw.get_time())
        self.uniform("u_campos", self.u_campos)
        self.render()
        self.render_ui()


def main():
    assert glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, "Demo", None, None)
    glfw.make_context_current(window)
    client = Client(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
