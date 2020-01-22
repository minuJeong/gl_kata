import glfw
from glm import *
import moderngl as mg
import numpy as np
from psd_tools import PSDImage
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


WIDTH, HEIGHT = 1024, 1024


class Scene(object):
    def __init__(self, window):
        super(Scene, self).__init__()
        self.window = window

        self.gl = mg.create_context()
        self.vb = self.gl.buffer(np.array([-1.0, -1.0, +1.0, -1.0, -1.0, +1.0, +1.0, +1.0], dtype=np.float32))
        self.ib = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))
        self.draginput = vec2(0.0, 0.0)

        self.compile()

        handler = FileSystemEventHandler()
        handler.on_modified = lambda e: self.set_need_compile()
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.schedule(handler, "./res", True)
        observer.start()

        self.is_drag = False
        self.prevpos = vec2(0.0, 0.0)

        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)

    def on_mouse_button(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                self.is_drag = True
                self.prevpos = vec2(*glfw.get_cursor_pos(window))
            elif action == glfw.RELEASE:
                self.is_drag = False

    def on_cursor_pos(self, window, x, y):
        pos = vec2(x, y)
        if self.is_drag:
            delta = pos - self.prevpos
            self.prevpos = vec2(x, y)
            self.draginput += delta

    def set_need_compile(self, is_needed=True):
        self.need_compile = is_needed

    def compile(self):
        self.need_compile = False
        try:
            VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
            self.program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            self.vao = self.gl.vertex_array(self.program, [(self.vb, "2f", "in_pos")], self.ib)
            psd_img = PSDImage.open("./res/tex.psd")
            self.texture = self.gl.texture(psd_img.size, 3, psd_img.compose().tobytes())
            self.texture.build_mipmaps()
            self.texture.use(0)

        except Exception as e:
            print(e)

    def uniform(self, uname, uvalue):
        if uname not in self.program:
            return

        if isinstance(uvalue, (int, float)):
            self.program[uname].value = uvalue
        elif isinstance(uvalue, (vec2, vec3, vec4)):
            self.program[uname].write(bytes(uvalue))
        elif isinstance(uvalue, (uvec2, uvec3, uvec4)):
            self.program[uname].write(bytes(uvalue))
        elif isinstance(uvalue, (ivec2, ivec3, ivec4)):
            self.program[uname].write(bytes(uvalue))

    def render(self):
        if self.need_compile:
            self.compile()
            return

        self.uniform("u_time", glfw.get_time())
        self.uniform("u_draginput", self.draginput)
        self.uniform("u_texture", 0)

        self.vao.render()


def start():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, "GLFW Window", None, None)
    glfw.make_context_current(window)
    scene = Scene(window)
    while not glfw.window_should_close(window):
        scene.render()
        glfw.poll_events()
        glfw.swap_buffers(window)

if __name__ == "__main__":
    start()
