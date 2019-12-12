import struct
from functools import reduce
from operator import add
from operator import mul

from glm import *
import glfw
import moderngl as mg

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def read(path):
    with open(path, "r") as fp:
        return fp.read()


class Game(object):
    def __init__(self, window, width, height):
        super(Game, self).__init__()
        self.window = window
        self.width, self.height = width, height

    def init(self):
        self.gl = mg.create_context()
        self.should_compile = True

        h = FileSystemEventHandler()
        h.on_modified = self.on_gl_mod
        o = Observer()
        o.schedule(h, "./gl", True)
        o.start()

    def compile(self):
        self.should_compile = False

        particle_dimension_unit = 96
        self.particles_dimension = ivec3(
            particle_dimension_unit, particle_dimension_unit, particle_dimension_unit
        )
        self.GX, self.GY, self.GZ = (
            self.particles_dimension[0] // 8,
            self.particles_dimension[1] // 8,
            self.particles_dimension[2] // 8,
        )

        num_particles = reduce(mul, self.particles_dimension)
        print(f"initializing with {num_particles} particles..")
        try:
            self.elapsed_frames = 0
            self.elapsed_time = 0.0
            self.prev_t = glfw.get_time()
            self.frametimes = [1.0]

            vbo_size = num_particles * (4 * 3) * 4
            print(f"vbo size: {vbo_size}")
            self.vbo = self.gl.buffer(reserve=vbo_size)
            self.vbo.bind_to_storage_buffer(0)

            self.compute_particles_init = self.gl.compute_shader(
                read("./gl/cs/particles_init.glsl")
            )
            self.compute_particles_update = self.gl.compute_shader(
                read("./gl/cs/particles_update.glsl")
            )

            self.program_background = self.gl.program(
                vertex_shader=read("./gl/vs/background.glsl"),
                fragment_shader=read("./gl/fs/background.glsl")
            )
            self.vbo_background = self.gl.buffer(struct.pack("8f", -1.0, -1.0, +1.0, -1.0, -1.0, +1.0, +1.0, +1.0))
            self.ibo_background = self.gl.buffer(struct.pack("6i", 0, 1, 2, 2, 1, 3))
            self.background_vao = self.gl.vertex_array(
                self.program_background,
                [(self.vbo_background, "2f", "in_pos")],
                self.ibo_background,
            )

            self.program_view = self.gl.program(
                vertex_shader=read("./gl/vs/view.glsl"),
                geometry_shader=read("./gl/gs/view.glsl"),
                fragment_shader=read("./gl/fs/view.glsl"),
            )
            self.render_vao = self.gl.vertex_array(
                self.program_view,
                [(self.vbo, "4f 4f 4f", "in_position", "in_velocity", "in_color")],
                skip_errors=True,
            )

            campos = vec3(-5.0, 5.0, -5.0)
            self.view = lookAt(campos, vec3(0.0), vec3(0.0, 1.0, 0.0))
            self.perspective = perspective(
                radians(74.0), self.width / self.height, 0.02, 100.0
            )

            print("\t ==== compiled shaders ====")

        except Exception as e:
            print(e)

    def uniform(self, p, n, v):
        if n in p:
            if isinstance(v, (vec2, vec3, ivec3, uvec3, vec4, mat4)):
                p[n].write(bytes(v))
            else:
                p[n].value = v

    def render(self):
        if self.should_compile:
            self.compile()

            self.uniform(
                self.compute_particles_init,
                "u_particles_dimension",
                self.particles_dimension,
            )

            self.uniform(
                self.compute_particles_update,
                "u_particles_dimension",
                self.particles_dimension,
            )

            self.compute_particles_init.run(self.GX, self.GY, self.GZ)

        t = glfw.get_time()
        frametime = t - self.prev_t
        if not self.elapsed_frames % 100:
            avr_ftime = reduce(add, self.frametimes) / len(self.frametimes)
            print(f"--- avr fps: {1.0 / avr_ftime:.2f}")
            self.frametimes = []
        else:
            self.frametimes.append(frametime)

        self.uniform(self.compute_particles_update, "u_time", t)
        self.uniform(self.program_view, "u_mvp", self.perspective * self.view)

        # self.compute_particles_update.run(self.GX, self.GY, self.GZ)

        self.gl.clear()
        self.background_vao.render()
        self.render_vao.render(mg.POINTS)

        self.elapsed_frames += 1
        self.elapsed_time += t
        self.prev_t = t

    def on_gl_mod(self, e):
        self.should_compile = True


def main():
    width, height = 512, 512

    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(width, height, "compute shader test", None, None)
    glfw.make_context_current(window)
    game = Game(window, width, height)
    game.init()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        game.render()
        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
