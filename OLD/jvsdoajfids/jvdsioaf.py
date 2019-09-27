import glfw
import moderngl as mg


class Render(object):
    def __init__(self):
        super(Render, self).__init__()

        self.GL = mg.create_context()
        self.vaos = []

    def read(self, path):
        with open(path, 'r') as fp:
            content = fp.read()

        for line in content.splitlines():
            if line.startswith("#include "):
                continue

    def recompile(self):
        self.require_recompile = False

        try:
            self.vaos.clear()
            program = self.GL.program()
            vao = self.GL.vertex_array(program, [(self.vbo, "4f", "in_pos")], self.ibo)
            self.vaos.append(vao)

            print("recompiled")

        except Exception as e:
            print(e)

    def render(self):
        if self.require_recompile:
            self.recompile()

        for vao in self.vaos:
            vao.render()


def main():
    glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(400, 300, "fvdsioaf", None, None)

    context = Render()

    while not glfw.window_should_close(window):

        context.render()

        glfw.swap_buffers(window)
        glfw.poll_events()


if __name__ == "__main__":
    main()
