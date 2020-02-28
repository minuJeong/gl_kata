import glfw

from const import WIDTH, HEIGHT, TITLE
from client import RenderClient


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    window = glfw.create_window(WIDTH, HEIGHT, TITLE, None, None)
    m = glfw.get_primary_monitor()
    x, y, w, h = glfw.get_monitor_workarea(m)
    glfw.set_window_pos(window, w // 2 - WIDTH // 2, h // 2 - HEIGHT // 2)
    glfw.make_context_current(window)
    client = RenderClient(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
