import glfw
import moderngl as mg

from scene import Scene


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window

        self.init()

    def init(self):
        self.gl = mg.create_context()

        self.scene = Scene(self.gl)

        self._compile()

    def _compile(self):
        self._need_compile = False
        try:
            self.scene.init()
            self.scene.camera.width, self.scene.camera.height = glfw.get_window_size(
                self.window
            )
            print("compiled")

        except Exception as e:
            print(e)

    def update(self):
        if self._need_compile:
            self._compile()
        self.scene.render()


if __name__ == "__main__":
    from main import main

    main()
