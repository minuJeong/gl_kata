import glfw
import moderngl as mg
import numpy as np


class Client(object):
    def __init__(self):
        super(Client, self).__init__()

        self.gl = mg.create_context()

    def compile(self):
        try:
            VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)

            print("compiled")

        except Exception as e:
            print(e)

    def update(self):
        pass


def main():
    glfw.init()
    window = glfw.create_window(1024, 1024, "", None, None)
    client = Client(window)
    while not glfw.window_should_close(window):
        glfw.swap_buffers(window)
        glfw.poll_events()
        client.update()

if __name__ == "__main__":
    main()
