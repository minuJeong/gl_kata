import glfw

from const import WIDTH, HEIGHT, TITLE
from client import RenderClient


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, TITLE, None, None)
    glfw.make_context_current(window)
    monitor = glfw.get_primary_monitor()
    x, y, w, h = glfw.get_monitor_workarea(monitor)
    ww, wh = glfw.get_window_size(window)
    glfw.set_window_pos(window, w // 2 - ww // 2, h // 2 - wh // 2)
    client = RenderClient(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
