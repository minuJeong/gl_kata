import glfw
import moderngl as mg
from pygltflib import GLTF2, Scene


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.init()

    def init(self):
        self.gl = mg.create_context()

        gltf = GLTF2()
        scene = Scene()

        gltf.scenes.append(scene)

        print(gltf)

    def update(self):
        pass


def main():
    WIDTH, HEIGHT = 1024, 1024
    glfw.init()
    window = glfw.create_window(WIDTH, HEIGHT, "", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.swap_buffers(window)
        glfw.poll_events()
        client.update()

if __name__ == '__main__':
    main()
