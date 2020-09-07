import glfw
import imgui
from imgui.integrations.base import BaseOpenGLRenderer
import moderngl as mg


class WaveFuncCollapse(object):
    def load_resources(self):
        self.gl = mg.create_context()
        imgui.create_context()
        self.imgui_render = BaseOpenGLRenderer()

    def generate(self):
        pass


def main():
    assert glfw.init()
    window = glfw.create_window(800, 800, "", None, None)
    glfw.make_context_current(window)

    wfc = WaveFuncCollapse()
    wfc.load_resources()
    wfc.generate()

if __name__ == "__main__":
    main()
