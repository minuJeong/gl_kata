import glfw
from glm import *

from client import RenderClient
from const import WIDTH, HEIGHT


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    window = glfw.create_window(WIDTH, HEIGHT, "hello, pyglm", None, None)
    glfw.make_context_current(window)
    client = RenderClient(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
