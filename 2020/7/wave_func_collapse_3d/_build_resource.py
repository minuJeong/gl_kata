import imgui
import numpy as np
import moderngl as mg
import glfw
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from imgui_integration import ModernGLGLFWRenderer


class Mode(object):
    BRUSH = 0


class Client(object):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.gl = mg.create_context()

        imgui.create_context()
        self.imgui_renderer = ModernGLGLFWRenderer(
            ctx=self.gl, display_size=glfw.get_window_size(window)
        )
        self.imgui_renderer.wire_events(self.gl, window)
        self.reload()

        def onmod(e):
            self.should_reload = True

        handler = FileSystemEventHandler()
        handler.on_modified = onmod
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

        self.input_text = ""
        self.is_press = False
        self.prev_cursor = (0, 0)

        self.imgui_renderer.on_mouse_button = self.on_mouse_button
        self.imgui_renderer.on_cursor_pos = self.on_cursor_pos
        self.imgui_renderer.on_key = self.on_key

    def on_mouse_button(self, window, button, action, mods):
        self.uniform("u_action", action)

        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                self.is_press = True
                self.prev_cursor = glfw.get_cursor_pos(window)
            elif action == glfw.RELEASE:
                self.is_press = False

    def on_cursor_pos(self, window, x, y):
        self.uniform("u_cursor", (x, y))

        w, h = glfw.get_window_size(window)
        dx, dy = x - self.prev_cursor[0], y - self.prev_cursor[1]
        dx, dy = dx / w, dy / h
        self.prev_cursor = (x, y)

        if self.is_press:
            pass
            # print(dx, dy)

    def on_resize(self, window, w, h):
        self.uniform("u_resolution", (w, h))

    def on_key(self, window, key, scancode, action, mods):
        self.uniform("u_key", key)
        self.uniform("u_key_action", action)
        self.uniform("u_key_mods", mods)

    def reload(self):
        self.should_reload = False
        try:
            VS, FS = open("./gl/quad.vs").read(), open("./gl/quad.fs").read()
            p = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            vertices = self.gl.buffer(
                np.array(
                    [[-1, -1, 0, 1], [+1, -1, 0, 1], [-1, +1, 0, 1], [+1, +1, 0, 1]],
                    dtype=np.float32,
                )
            )
            indices = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))
            self.quad = self.gl.vertex_array(p, [(vertices, "4f", "in_pos")], indices)

            RESOLUTION = 4
            VOXEL_DATA_SIZE = 1
            self.voxel = self.gl.buffer(
                reserve=RESOLUTION * RESOLUTION * RESOLUTION * VOXEL_DATA_SIZE
            )
            self.voxel.bind_to_storage_buffer(0)

            self.uniform("u_resolution", glfw.get_window_size(self.window))

            print("reloaded")

        except Exception as e:
            print(e)

    def uniform(self, uname, uvalue):
        if not self.quad or uname not in self.quad.program:
            return

        p = self.quad.program
        p[uname] = uvalue

    def update(self):
        if self.should_reload:
            self.reload()
            return

        self.uniform("u_time", glfw.get_time())

        self.quad.render()
        self.render_ui()

    def render_ui(self):
        imgui.new_frame()
        imgui.begin("")
        if imgui.button("capture"):
            pass

        if imgui.button("brush"):
            self.mode = Mode.BRUSH

        changed, self.input_text = imgui.input_text("input", self.input_text, 255)
        if changed:
            pass

        imgui.end()
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())


def main():
    assert glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(800, 800, "", None, None)
    glfw.make_context_current(window)
    client = Client(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
