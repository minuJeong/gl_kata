import moderngl as mg
import glfw
import glm
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Render(object):
    def __init__(self):
        super(Render, self).__init__()

    def uniform(self, data):
        for p in [self.program, self.verts_cs]:
            for n, v in data.items():
                if n not in p:
                    continue

                p[n].value = v

    def read(self, path):
        with open(path, "r") as fp:
            context = fp.read()

        lines = []
        for line in context.splitlines():
            if not line.startswith("#include "):
                lines.append(line)
                continue

            path = line.split("#include ")[1]
            lines.append(self.read(path))

        return "\n".join(lines)

    def regenerate_verts_content(self):
        return [(self.vbo, "3f", "in_pos"), (self.normals_bo, "3f", "in_normal")]

    def initialize_gl(self):
        self.gl = mg.create_context()
        self.gl.disable(mg.CULL_FACE)

        NUM_VERTICES = 8
        NUM_QUADS = 6

        self.vbo = self.gl.buffer(reserve=NUM_VERTICES * 3 * 4)
        self.vbo.bind_to_storage_buffer(0)
        self.normals_bo = self.gl.buffer(reserve=NUM_VERTICES * 3 * 4)
        self.normals_bo.bind_to_storage_buffer(1)

        self.ibo = self.gl.buffer(reserve=3 * 2 * NUM_QUADS * 4)
        self.ibo.bind_to_storage_buffer(2)

        self.vbo_content = self.regenerate_verts_content()

        self.recompile_vao()

        def on_mod(e):
            self.should_recompile_vao = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_mod
        observer = Observer()
        observer.schedule(handler, "./gl")
        observer.start()

    def recompile_vao(self):
        self.should_recompile_vao = False

        try:

            self.program = self.gl.program(
                vertex_shader=self.read("./gl/vertices.glsl"),
                fragment_shader=self.read("./gl/fragments.glsl"),
            )
            self.verts_cs = self.gl.compute_shader(
                self.read("./gl/vertex_factory.glsl")
            )

            self.vao = self.gl.vertex_array(
                self.program, self.vbo_content, self.ibo, skip_errors=True
            )

            print("recompiled")

        except Exception as e:
            print(e)

    def paint_gl(self):
        self.vao.render()

    def set_mvp(self):
        def iter_mat4(m):
            for i in range(4):
                for j in range(4):
                    yield m[i][j]

        self.uniform(
            {
                "u_MVP": tuple(iter_mat4(self.MVP))
            }
        )

    def start(self):
        glfw.init()
        glfw.window_hint(glfw.FLOATING, glfw.TRUE)
        self.window = glfw.create_window(400, 400, "Hello, GLFW", None, None)
        glfw.make_context_current(self.window)

        self.pressing_keys = []
        glfw.set_key_callback(self.window, self.on_key)
        self.initialize_gl()

        self.cam_pos = glm.vec3(0.0, 0.0, -5.0)
        self.model = glm.identity(glm.mat4)
        self.view = glm.lookAt(self.cam_pos, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
        self.projection = glm.perspective(glm.radians(94.0), 1.0 / 1.0, 0.1, 100.0)
        self.MVP = self.projection * self.view * self.model

        prev_t = glfw.get_time()
        while not glfw.window_should_close(self.window):
            self.gl.clear()

            if self.should_recompile_vao:
                self.recompile_vao()

            t = glfw.get_time()
            self.uniform({"u_time": t})

            self.cpu_tick(t - prev_t)
            prev_t = t

            self.verts_cs.run()
            self.set_mvp()
            self.paint_gl()

            glfw.poll_events()
            glfw.swap_buffers(self.window)

    def on_key(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            self.pressing_keys.append(key)

        elif action == glfw.RELEASE:
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(self.window, glfw.TRUE)

            if key in self.pressing_keys:
                self.pressing_keys.remove(key)

    def cpu_tick(self, elapsed_time):
        SPD = 5.0

        is_MVP_dirty = False
        for key in self.pressing_keys:
            if key == glfw.KEY_LEFT or key == glfw.KEY_A:
                self.view = glm.rotate(self.view, +SPD * elapsed_time, glm.vec3(0.0, 1.0, 0.0))
                is_MVP_dirty = True
            elif key == glfw.KEY_RIGHT or key == glfw.KEY_D:
                self.view = glm.rotate(self.view, -SPD * elapsed_time, glm.vec3(0.0, 1.0, 0.0))
                is_MVP_dirty = True
            elif key == glfw.KEY_UP or key == glfw.KEY_W:
                self.view = glm.rotate(self.view, +SPD * elapsed_time, glm.vec3(0.0, 0.0, 1.0))
                is_MVP_dirty = True
            elif key == glfw.KEY_DOWN or key == glfw.KEY_S:
                self.view = glm.rotate(self.view, -SPD * elapsed_time, glm.vec3(0.0, 0.0, 1.0))
                is_MVP_dirty = True

        if is_MVP_dirty:
            is_MVP_dirty = False
            self.MVP = self.projection * self.view * self.model


def main():
    render = Render()
    render.start()


if __name__ == "__main__":
    main()
