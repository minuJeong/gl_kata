import glfw

from gfx import GFX


class Client(object):
    def __init__(self, window):
        super().__init__()
        self.gfx = GFX()
        self.window = window

        self.gfx.init()

    def tick(self, elapsed_time, delta_time):
        self.gfx.tick(elapsed_time, delta_time)


def main():
    assert glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(800, 600, "", None, None)
    glfw.make_context_current(window)
    client = Client(window)

    prev_t = 0
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        t = glfw.get_time()
        client.tick(t, t - prev_t)
        prev_t = t


if __name__ == "__main__":
    main()
