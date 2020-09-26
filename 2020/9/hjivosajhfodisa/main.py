import glfw
import moderngl as mg


class Client(object):
    def __init__(self, window):
        super().__init__()

        self.window = window

    def start(self):
        self.gl = mg.create_context()

    def compile(self):
        try:

            print("compiled")

        except Exception as e:
            print(e)

    def update(self):
        pass


def main():
    assert glfw.init()
    window = glfw.create_window(512, 512, "", None, None)
    glfw.make_context_current(window)
    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
