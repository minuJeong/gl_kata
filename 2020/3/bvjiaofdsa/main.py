import glfw

from const import WIDTH, HEIGHT, TITLE
from client import Client


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, TITLE, None, None)
    glfw.make_context_current(window)
    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()

if __name__ == '__main__':
    main()
