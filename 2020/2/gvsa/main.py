import glfw
import moderngl as mg
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


WIDTH, HEIGHT = 800, 600
UP = vec3(0.0, 1.0, 0.0)
RIGHT = vec3(1.0, 0.0, 0.0)


scene_def = [
    ("./gl/mesh/mesh_builder_0.glsl", "./gl/mesh/mesh_updater_0.glsl", "./gl/vs/vs_0.glsl", "./gl/fs/fs_0.glsl"),
]


def _flatmat(m):
    _f = []
    for v in m:
        _f.extend((*v,))
    return tuple(_f)


class Mesh(object):
    def __init__(self, gl, builder, updater, vs, fs):
        super(Mesh, self).__init__()
        BUILDER, UPDATER = open(builder).read(), open(updater).read()
        VS, FS = open(vs).read(), open(fs).read()

        vb = gl.buffer(reserve=8 * (4 + 4) * 4)
        ib = gl.buffer(reserve=6 * 6 * 4)
        vb.bind_to_storage_buffer(0)
        ib.bind_to_storage_buffer(1)

        self.builder = gl.compute_shader(BUILDER)
        self.updater = gl.compute_shader(UPDATER)
        self.program = gl.program(vertex_shader=VS, fragment_shader=FS)
        self.builder.run(1)

        self.node = gl.vertex_array(self.program, [(vb, "4f 4f", "in_pos", "in_normal")], ib, skip_errors=True)

        self.m = translate(mat4(1.0), vec3(0.0, 0.0, -6.0))
        self.vp = perspective(radians(74.0), WIDTH / HEIGHT, 0.01, 100.0)

        self.uniform("m", _flatmat(self.m))
        self.uniform("vp", _flatmat(self.vp))

    def uniform(self, uname, uvalue):
        if uname not in self.program:
            return

        self.program[uname] = uvalue

    def render(self):
        if self.updater:
            self.updater.run(1)

        t = glfw.get_time()

        self.m = rotate(self.m, 0.06, mix(UP, RIGHT, cos(t * 3.0) * 0.5 + 0.5))
        self.uniform("m", _flatmat(self.m))
        self.node.render()


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()

        self.gl = mg.create_context()
        self.compile()

        hand = FileSystemEventHandler()
        hand.on_modified = lambda e: self.set_need_compile()
        observer = Observer()
        observer.schedule(hand, "./gl", True)
        observer.start()

    def set_need_compile(self):
        self._need_compile = True

    def compile(self):
        self._need_compile = False
        try:
            self.scene = []

            for node in scene_def:
                assert len(node) == 4
                mesh = Mesh(self.gl, *node)
            self.scene.append(mesh)

            print("compiled")

        except Exception as e:
            print(e)

    def uniform(self, uname, uvalue):
        for node in self.scene:
            node.uniform(uname, uvalue)

    def update(self):
        if self._need_compile:
            self.compile()

        self.uniform("u_time", glfw.get_time())

        self.gl.clear()
        self.gl.enable(mg.DEPTH_TEST)
        for node in self.scene:
            node.render()


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, "hello", None, None)
    glfw.make_context_current(window)
    client = Client(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
