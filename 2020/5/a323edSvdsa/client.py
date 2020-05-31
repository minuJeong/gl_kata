# from OpenGL.GL import glFlush
import moderngl as mg
import glfw
from glm import *
import imgui
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from mesh import Quad
from integrations.imgui import ModernGLRenderer


# precompile imgui code
IMGUI_CODE = compile(
    """
imgui.new_frame()
if imgui.begin_main_menu_bar():
    if imgui.begin_menu("File", True):
        clicked_quit, selected_quit = imgui.menu_item("Quit", "ctrl+Q", False, True)
        if clicked_quit:
            self.close()
        imgui.end_menu()
    imgui.end_main_menu_bar()

imgui.begin("Control")
imgui.text(f"FPS: {1.0 / self.frame_time:.2f}")
t, self.u_camera_rotation_xz = imgui.slider_float("CAM_XZ", self.u_camera_rotation_xz, 0.0, 6.283)
if t:
    self.uniform("u_camera_rotation_xz", self.u_camera_rotation_xz)
t, self.u_camera_zoom = imgui.slider_float("CAM_ZOOM", self.u_camera_zoom, 0.5, 12.566)
if t:
    self.uniform("u_camera_zoom", self.u_camera_zoom)

imgui.end()
imgui.render()
""",
    "fake_module",
    "exec",
)


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()

        self.window = window
        glfw.make_context_current(window)

        self.gl = mg.create_context()
        self.need_compile = False

        imgui.create_context()
        win_size = glfw.get_window_size(window)
        self.imgui = ModernGLRenderer(ctx=self.gl, display_size=win_size)

        quad = Quad(self.gl, vspath="./gl/quad.vs", fspath="./gl/quad.fs")

        self.children = []
        self.children.append(quad)

        def onmod(e):
            self.need_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = onmod
        shader_code_observer = Observer()
        shader_code_observer.schedule(handler, "./gl", True)
        shader_code_observer.start()

        self.wire_glfw_to_imgui_events()

        self.last_time = 0
        self.u_camera_rotation_xz = 0.0
        self.u_camera_zoom = 1.0

    def wire_glfw_to_imgui_events(self):
        def resize(window, width, height):
            self.gl.viewport = (0, 0, width, height)
            imgui.get_io().display_size = width, height

        def on_cursor_pos(window, x, y):
            imgui.get_io().mouse_pos = x, y

        def on_mouse_button(window, button, action, mods):
            imgui.get_io().mouse_down[button] = action

        def on_scroll(window, scroll_x, scroll_y):
            imgui.get_io().mouse_wheel = scroll_y

        glfw.set_window_size_callback(self.window, resize)
        glfw.set_cursor_pos_callback(self.window, on_cursor_pos)
        glfw.set_mouse_button_callback(self.window, on_mouse_button)
        glfw.set_scroll_callback(self.window, on_scroll)

    def update(self):
        if self.need_compile:
            self.compile_shaders()

        t = glfw.get_time()
        self.uniform("u_time", t)

        self.render()
        self.render_ui()

        # should only be used with single buffered glfw window
        # glFlush()

    def uniform(self, uname, uvalue):
        for child in self.children:
            child.uniform(uname, uvalue)

    def compile_shaders(self):
        self.need_compile = False
        for child in self.children:
            child.compile_shaders()

    def render(self):
        for child in self.children:
            child.render()

    def render_ui(self):
        t = glfw.get_time()
        self.frame_time = t - self.last_time

        exec(IMGUI_CODE)

        self.last_time = t
        self.imgui.render(imgui.get_draw_data())

    def close(self):
        glfw.set_window_should_close(self.window, glfw.TRUE)


if __name__ == "__main__":
    from main import main

    main()
