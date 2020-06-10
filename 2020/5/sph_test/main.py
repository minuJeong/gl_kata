import glfw

from client import Client


def main():
    assert glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)

    window = glfw.create_window(800, 600, "SPH", None, None)

    glfw.make_context_current(window)

    c = Client(window)

    while not glfw.window_should_close(window):

        glfw.swap_buffers(window)

        glfw.poll_events()

        c.update()


if __name__ == "__main__":
    main()
