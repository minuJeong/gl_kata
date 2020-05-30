import moderngl as mg
import glfw
from glm import *
import imgui
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from mesh import Quad
from integrations.imgui import ModernGLRenderer


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

    def wire_glfw_to_imgui_events(self):
        window = self.window
        io = imgui.get_io()

        def resize(width: int, height: int):
            nonlocal io
            io.display_size = width, height

        def on_cursor_pos(window, x, y):
            nonlocal io
            io.mouse_pos = x, y

        def on_mouse_button(window, button, action, mods):
            nonlocal io
            io.mouse_down[button] = action

        def on_scroll(window, scroll_x, scroll_y):
            nonlocal io
            io.mouse_wheel = scroll_y

        glfw.set_window_size_callback(window, resize)
        glfw.set_cursor_pos_callback(window, on_cursor_pos)
        glfw.set_mouse_button_callback(window, on_mouse_button)
        glfw.set_scroll_callback(window, on_scroll)

    def update(self):
        if self.need_compile:
            self.compile_shaders()

        self.render()
        self.render_ui()

    def compile_shaders(self):
        for child in self.children:
            child.compile_shaders()

    def render(self):
        for child in self.children:
            child.render()

    def render_ui(self):
        imgui.new_frame()
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):
                clicked_quit, selected_quit = imgui.menu_item("Quit", "ctrl+Q", False, True)
                if clicked_quit:
                    self.close()
                imgui.end_menu()
            imgui.end_main_menu_bar()

        imgui.begin("Control")
        imgui.button("Hello")
        imgui.end()
        imgui.render()
        self.imgui.render(imgui.get_draw_data())

    def close(self):
        glfw.set_window_should_close(self.window, glfw.TRUE)


if __name__ == "__main__":
    from main import main

    main()
