import glfw

from const import WIDTH, HEIGHT


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()

    def update(self):
        pass


def main():
    assert glfw.init()
    window = glfw.create_window(WIDTH, HEIGHT, "", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.swap_buffers(window)
        glfw.poll_events()
        client.update()

if __name__ == "__main__":
    main()
