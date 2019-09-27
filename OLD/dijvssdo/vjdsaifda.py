import moderngl as mg
import glfw

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


GL = None


def read_file(path):
    with open(path, "r") as fp:
        content = fp.read()

    lines = []
    for line in content.splitlines():
        if not line.startswith("#include "):
            lines.append(line)
            continue

        print(line.replace("#include ", ""))
        included_content = read_file(line.replace("#include ", "").replace("\n", ""))
        lines.append(included_content)

    joined_file = "\n".join(lines)
    return joined_file


class DisplayObject(object):
    def __init__(self):
        super(DisplayObject, self).__init__()
        self.vao = None
        self.children = []

    def build_vao(self):
        raise Exception("VAO building not specified")

    def render(self):
        if not self.vao:
            return

        for child in self.children:
            child.render()

        self.vao.render()


class ScreenQuad(DisplayObject):
    def __init__(self, auto_rebuild=False):
        super(ScreenQuad, self).__init__()
        self.auto_rebuild = auto_rebuild

        self.build_mesh()
        self.build_vao()

    def build_mesh(self):
        global GL

        COUNT_VERTICES = 4
        VBO_DIMENSION = 2
        COUNT_INDICES = 6
        BYTE_SIZE = 4

        self.vbo = GL.buffer(reserve=COUNT_VERTICES * VBO_DIMENSION * BYTE_SIZE)
        self.vbo_content = [(self.vbo, f"{VBO_DIMENSION}f", "in_pos")]
        self.ibo = GL.buffer(reserve=COUNT_INDICES * BYTE_SIZE)

        self.vbo.bind_to_storage_buffer(0)
        self.ibo.bind_to_storage_buffer(1)

        mesh_builder_cs = GL.compute_shader(read_file("./gl/mesh_builder_cs.glsl"))
        mesh_builder_cs.run()

    def rebuild_vao(self, e=None):
        global GL

        self.require_rebuild = False


        fs_file = read_file("./gl/frags.glsl")
        print(fs_file)

        def build_vao():
            program = GL.program(
                vertex_shader=read_file("./gl/verts.glsl"),
                fragment_shader=read_file("./gl/frags.glsl"),
            )

            self.vao = GL.vertex_array(
                program, self.vbo_content, self.ibo, skip_errors=True
            )

        try:
            build_vao()
            print("rebuilt vao.")

        except Exception as e:
            print("Failed to rebuild vao, because: ", e)

    def build_vao(self):
        self.rebuild_vao()

        def on_mod(e=None):
            self.require_rebuild = True

        if self.auto_rebuild:
            handler = FileSystemEventHandler()
            handler.on_modified = on_mod
            observer = Observer()
            observer.schedule(handler, "./gl/")
            observer.start()

    def render(self):
        super(ScreenQuad, self).render()

        if self.require_rebuild:
            self.rebuild_vao()


class Scene(object):
    def __init__(self):
        super(Scene, self).__init__()
        self.children = []

    def add_child(self, child: DisplayObject):
        self.children.append(child)

    def render(self):
        for child in self.children:
            child.render()


class Renderer(object):
    def __init__(self):
        super(Renderer, self).__init__()

    def recompile_vao(self):
        screen_quad = ScreenQuad(True)
        self.scene.add_child(screen_quad)

    def init(self):
        global GL

        self.scene = Scene()
        GL = mg.create_context()
        self.recompile_vao()

    def render(self):
        self.scene.render()

    def start_mainloop(self):
        glfw.init()
        glfw.window_hint(glfw.FLOATING, glfw.TRUE)
        glfw_window = glfw.create_window(400, 400, "Hello", None, None)
        glfw.make_context_current(glfw_window)

        self.init()

        while not glfw.window_should_close(glfw_window):

            self.render()

            glfw.poll_events()
            glfw.swap_buffers(glfw_window)


def main():
    renderer = Renderer()
    renderer.start_mainloop()


if __name__ == "__main__":
    main()
