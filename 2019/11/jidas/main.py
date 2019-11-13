import numpy as np
import moderngl as mg
import glfw

_any = any
from glm import *


class VectorFieldInfo(object):
    def __init__(self, width, height, depth):
        super(VectorFieldInfo, self).__init__()

        self.width, self.height, self.depth = width, height, depth

        # vec4 velocity
        self.components_per_grid = 4

        # constant
        self.precision = 4

    def get_grid_size(self):
        return self.width * self.height * self.depth

    def get_size(self):
        return self.get_grid_size() * self.components_per_grid * self.precision


def read_file(path):
    with open(path, "r") as fp:
        return fp.read()


class Render(object):
    BINARY_TYPES = (
        [vec2, vec3, vec4]
        + [uvec2, uvec3, uvec4]
        + [ivec2, ivec3, ivec4]
        + [mat2, mat3, mat4]
    )

    def __init__(self, width, height):
        super(Render, self).__init__()

        self.width, self.height = width, height

        self.gl = mg.create_context()

        n_particles = 256 * 64

        width, height, depth = 32, 32, 32
        vector_field_info = VectorFieldInfo(width, height, depth)

        particles_data = np.zeros(shape=(n_particles, 12))
        particles_data[:, 0:3] = np.random.uniform(-1.0, +1.0, particles_data[:, 0:3].shape)
        particles_data[:, 3] = 1.0

        self.particles = self.gl.buffer(particles_data.astype(np.float32).tobytes())
        self.particles.bind_to_storage_buffer(0)
        self.vector_field = self.gl.buffer(reserve=vector_field_info.get_size())
        self.vector_field.bind_to_storage_buffer(1)

        self.cs = self.gl.compute_shader(read_file("./gl/advance_particles.glsl"))

        self.uniform(self.cs, {"u_grid_res": uvec3(width, height, depth)})
        self.gx = n_particles // 64

        self.particles_prog = self.gl.program(
            vertex_shader=read_file("./gl/passthrough.vert.glsl"),
            geometry_shader=read_file("./gl/particle_to_quad.geo.glsl"),
            fragment_shader=read_file("./gl/color.frag.glsl"),
        )

        self.particles_va = self.gl.vertex_array(
            self.particles_prog,
            [(self.particles, "4f 4f", "in_pos", "in_vel")],
            skip_errors=True,
        )

        self.screen_program = self.gl.program(
            vertex_shader=read_file("./gl/screen_verts.glsl"),
            fragment_shader=read_file("./gl/screen_frag.glsl"),
        )

        self.screen_vbo = self.gl.buffer(
            np.array([-1.0, -1.0, +1.0, -1.0, -1.0, +1.0, +1.0, +1.0])
            .astype(np.float32)
            .tobytes()
        )

        self.screen_ibo = self.gl.buffer(
            np.array([0, 1, 2, 2, 1, 3]).astype(np.int32).tobytes()
        )

        self.screen_va = self.gl.vertex_array(
            self.screen_program, [(self.screen_vbo, "2f", "in_pos")], self.screen_ibo
        )

        self.uniform(self.particles_prog, {"u_aspect": width / height})

    def uniform(self, p, data):
        for n, v in data.items():
            if n in p:
                if _any(filter(lambda t: isinstance(v, t), Render.BINARY_TYPES)):
                    p[n].write(bytes(v))
                else:
                    p[n].value = v

    def render(self):
        self.gl.clear()

        self.uniform(self.cs, {"u_time": glfw.get_time()})
        self.uniform(self.particles_prog, {"u_time": glfw.get_time()})

        self.cs.run(self.gx)
        # self.screen_va.render()
        self.particles_va.render(mg.POINTS)

    def on_size(self, window, width, height):
        self.width, self.height = width, height
        self.gl.viewport = (0, 0, width, height)
        self.uniform(self.particles_prog, {"u_aspect": width / height})

    def on_mousepos(self, window, x, y):
        u, v = x / self.width, y / self.height
        u, v = u * 2.0 - 1.0, v * 2.0 - 1.0
        v = -v
        self.uniform(self.cs, {"u_cursor": vec2(u, v)})


def main():
    glfw.init()

    width, height = 960, 960

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(width, height, "particles test", None, None)
    glfw.make_context_current(window)

    render = Render(width, height)
    glfw.set_window_size_callback(window, render.on_size)
    glfw.set_cursor_pos_callback(window, render.on_mousepos)

    while not glfw.window_should_close(window):
        render.render()

        glfw.swap_buffers(window)
        glfw.poll_events()


if __name__ == "__main__":
    main()
