import glfw

from client import MyClient
from const import WIDTH, HEIGHT


def main():
    assert glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, "", None, None)
    glfw.make_context_current(window)

    client = MyClient(window)
    while not glfw.window_should_close(window):
        glfw.swap_buffers(window)
        glfw.poll_events()
        client.update()


if __name__ == "__main__":
    main()
