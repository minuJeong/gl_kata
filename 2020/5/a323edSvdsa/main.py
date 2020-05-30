import glfw

from client import Client


def main():
    assert glfw.init()
    # glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    w = glfw.create_window(800, 600, "", None, None)
    c = Client(w)

    while not glfw.window_should_close(w):
        glfw.poll_events()
        c.update()
        glfw.swap_buffers(w)


if __name__ == "__main__":
    main()
