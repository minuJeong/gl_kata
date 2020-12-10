import glfw

from client import Client


def main():
    assert glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(512, 512, "", None, None)
    glfw.make_context_current(window)
    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.swap_buffers(window)
        glfw.poll_events()
        client.update()

    client.on_close()

if __name__ == '__main__':
    main()
