import moderngl as mg
import glfw


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()
        self.window = window

        self.gl = mg.create_context()
        self.compile()

    def compile(self):
        self.need_compile = False
        try:
            self.num_particles = 1 * 1
            particles = self.gl.buffer(reserve=self.num_particles * (4 + 4 + 1 + 1 + 1) * 4)
            vb = self.gl.buffer(reserve=self.num_particles * (4 * (4 + 2 + 1)) * 4)
            ib = self.gl.buffer(reserve=self.num_particles * 6 * 4)

            vb.bind_to_storage_buffer(0)
            ib.bind_to_storage_buffer(1)
            particles.bind_to_storage_buffer(2)

            self.cs_init_vertices = self.gl.compute_shader(
                open("./gl/init_vertices.glsl").read()
            )
            self.cs_particle_advant = self.gl.compute_shader(
                open("./gl/particle_advant.glsl").read()
            )

            VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
            self.p_render = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            self.va_render = self.gl.vertex_array(
                self.p_render,
                [(vb, "4f 2f 1u", "in_pos", "in_uv", "in_id")],
                ib,
                skip_errors=True,
            )

            self.cs_init_vertices.run(self.num_particles // 64 + 1)
            print("compiled")

        except Exception as e:
            print(e)

    def update(self):
        if self.need_compile:
            return self.compile()

        self.cs_particle_advant.run(self.num_particles // 64 + 1)
        self.va_render.render()


def main():
    WIDTH, HEIGHT = 512, 512
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, "particles!", None, None)
    glfw.make_context_current(window)
    client = Client(window)
    while not glfw.window_should_close(window):
        client.update()
        glfw.poll_events()
        glfw.swap_buffers(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
