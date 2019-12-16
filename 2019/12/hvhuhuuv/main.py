import os
import struct

from glm import *
import glfw
import moderngl as mg
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


UP = vec3(0.0, 1.0, 0.0)
RIGHT = vec3(1.0, 0.0, 0.0)
FORWARD = vec3(0.0, 0.0, 1.0)


def read(path):
    with open(path, "r") as fp:
        return fp.read()


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()

        self.window = window
        self.width, self.height = glfw.get_window_size(window)

        self.gl = mg.create_context()
        self.compile()

        self.camerapos = vec4(0.0, 0.0, 20.0, 1.0)

        def on_modified(e):
            # restart python if python code is changed
            if e.src_path.endswith(".py"):
                glfw.set_window_should_close(window, glfw.TRUE)
                os.system(f"python {e.src_path}")

            # compile shaders if the change is not python code
            else:
                self.should_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_modified
        observer = Observer()
        observer.schedule(handler, "./.", True)
        observer.start()

        self.is_drag_rot_cam = False
        self.prempos = vec2(0.0, 0.0)

        # wire glfw events
        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)
        glfw.set_scroll_callback(window, self.on_scroll)
        glfw.set_window_size_callback(window, self.on_window_size)

    def on_mouse_button(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                self.is_drag_rot_cam = True

                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE)
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
            else:
                self.is_drag_rot_cam = False
                glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.FALSE)
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def on_cursor_pos(self, window, x, y):
        delta = vec2(x, y) - self.prempos

        if self.is_drag_rot_cam:
            p = self.camerapos

            rotation_x = rotate(mat4(1.0), -delta.x * 0.001, UP)
            p = rotation_x * p
            # p.y += delta.y

            self.camerapos = p

        self.prempos = vec2(x, y)

    def on_scroll(self, window, x, y):
        forward = normalize(vec3(self.camerapos.x, 0.0, self.camerapos.z))
        p = self.camerapos.xyz
        p -= forward * y * 4.0
        if length(p) > 10.0:
            # self.camerapos = vec4(p, self.camerapos.w)
            pass

    def on_window_size(self, window, w, h):
        self.width, self.height = w, h
        self.gl.viewport = (0, 0, w, h)
        self.uniform("u_aspect", w / h)

    def compile(self):
        self.should_compile = False
        try:
            vs, fs = read("./gl/quad.vs"), read("./gl/quad.fs")
            self.program = self.gl.program(vertex_shader=vs, fragment_shader=fs)

            vb = self.gl.buffer(
                struct.pack(
                    "16f",
                    *[-1.0, -1.0, 0.0, 1.0,],
                    *[+1.0, -1.0, 0.0, 1.0,],
                    *[-1.0, +1.0, 0.0, 1.0,],
                    *[+1.0, +1.0, 0.0, 1.0,]
                )
            )

            ib = self.gl.buffer(struct.pack("6i", 0, 1, 2, 2, 1, 3))

            content = [(vb, "4f", "in_pos")]

            self.vao = self.gl.vertex_array(self.program, content, ib)

            self.uniform("u_aspect", self.width / self.height)

            print("compiled")

        except Exception as e:
            print(e)

    def uniform(self, uname, uvalue):
        if uname not in self.program:
            return

        uniform = self.program[uname]
        if isinstance(uvalue, (float, int)):
            uniform.value = uvalue
        else:
            uniform.write(bytes(uvalue))

    def update(self):
        if self.should_compile:
            self.compile()

        t = glfw.get_time()

        self.uniform("u_camerapos", self.camerapos)
        self.uniform("u_time", t)
        self.vao.render()


def main():
    width, height = 1920, 1280
    width, height = width // 2, height // 2

    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(width, height, "volume sculpt", None, None)
    glfw.make_context_current(window)
    client = Client(window)
    while not glfw.window_should_close(window):
        client.update()
        glfw.poll_events()
        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
