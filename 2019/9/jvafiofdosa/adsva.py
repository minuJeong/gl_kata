import glm
import glfw
import moderngl as mg

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Renderer(object):
    def read(self, path):
        with open(path, "r") as fp:
            content = fp.read()

        lines = []
        for line in content.splitlines():
            if not line.startswith("#include "):
                lines.append(line)
                continue

            path = line.split("#include ")[1]
            lines.append(self.read(path))

        return "\n".join(lines)

    def recompile(self):
        self.should_recompile = False

        try:
            vertex_shader = self.read("./gl/vertex_shader.glsl")
            fragment_shader = self.read("./gl/fragment_shader.glsl")
            program = self.gl.program(
                vertex_shader=vertex_shader, fragment_shader=fragment_shader
            )
            vao = self.gl.vertex_array(program, [(self.vbo, "4f", "in_pos")], self.ibo)

            self.vaos = []
            self.programs = []

            self.programs.append(program)
            self.vaos.append(vao)

            self.uniform({
                "u_resolution": (self.u_width, self.u_height),
                "u_input_move": self.input_move,
            })
            print("compiled shaders")

        except Exception as e:
            print(e)

    def uniform(self, data):
        for p in self.programs:
            for n, v in data.items():
                if n in p:
                    p[n].value = v

    def __init__(self, width, height):
        super(Renderer, self).__init__()

        self.u_width, self.u_height = width, height
        self.input_move = (0.0, 0.0)

        self.vaos = []
        self.programs = []

        self.gl = mg.create_context()

        self.vbo = self.gl.buffer(reserve=4 * 4 * 4)
        self.ibo = self.gl.buffer(reserve=6 * 4)

        self.vbo.bind_to_storage_buffer(0)
        self.ibo.bind_to_storage_buffer(1)

        cs_screen_mesh = self.read("./gl/compute_screen_mesh.glsl")
        cs = self.gl.compute_shader(cs_screen_mesh)
        cs.run(1)

        self.recompile()

        def on_mod(e):
            self.should_recompile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_mod
        observer = Observer()
        observer.schedule(handler, "./gl/")
        observer.start()

    def render(self, t):
        if self.should_recompile:
            self.recompile()

        self.uniform({"u_time": t})

        for vao in self.vaos:
            vao.render()

    def update_input_move(self, input_move):
        self.input_move = input_move
        self.uniform({"u_input_move": input_move})


class InputManager(object):
    def __init__(self, renderer):
        super(InputManager, self).__init__()
        self.renderer = renderer
        self.pressing_keys = []

        self.move = glm.vec2(0.0, 0.0)

    def on_key_press(self, window, key):
        if key not in self.pressing_keys:
            self.pressing_keys.append(key)

    def on_key_release(self, window, key):
        if key in self.pressing_keys:
            self.pressing_keys.remove(key)

    def on_key(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            self.on_key_press(window, key)

        elif action == glfw.RELEASE:
            self.on_key_release(window, key)

    def update(self):
        for key in self.pressing_keys:
            self._update_key(key)

    def _update_key(self, key):
        is_dirty = False

        MOVE_SPD = 0.02
        if key == glfw.KEY_A:
            self.move.x += MOVE_SPD
            is_dirty = True

        elif key == glfw.KEY_W:
            self.move.y += MOVE_SPD
            is_dirty = True

        elif key == glfw.KEY_D:
            self.move.x -= MOVE_SPD
            is_dirty = True

        elif key == glfw.KEY_S:
            self.move.y -= MOVE_SPD
            is_dirty = True

        MOVEMENT_CONSTRAINT = 0.8
        self.move = glm.clamp(self.move, glm.vec2(-MOVEMENT_CONSTRAINT), glm.vec2(MOVEMENT_CONSTRAINT))

        if is_dirty:
            self.renderer.update_input_move((self.move.x, self.move.y))


def main():
    width, height = 600, 400
    title = "hello world"

    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(width, height, title, None, None)
    glfw.make_context_current(window)

    renderer = Renderer(width, height)
    input_manager = InputManager(renderer)

    glfw.set_key_callback(window, input_manager.on_key)

    while not glfw.window_should_close(window):

        renderer.render(glfw.get_time())
        input_manager.update()

        glfw.swap_buffers(window)
        glfw.poll_events()


if __name__ == "__main__":
    main()
