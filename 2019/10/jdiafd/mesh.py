from util import Util


class Mesh(object):
    def __init__(self, cs, vs, fs):
        super(Mesh, self).__init__()
        self.compute_shader = cs
        self.vertex_shader, self.fragment_shader = vs, fs
        self.vao = None

    def compile(self, gl):
        vbo = gl.buffer(reserve=8 * 4 * 4)
        ibo = gl.buffer(reserve=6 * 2 * 3)
        vbo.bind_to_storage_buffer(0)
        ibo.bind_to_storage_buffer(1)

        cs = gl.compute_shader(Util.load_shader(self.compute_shader))
        cs.run(1)

        program = gl.program(
            vertex_shader=Util.load_shader(self.vertex_shader),
            fragment_shader=Util.load_shader(self.fragment_shader),
        )
        self.vao = gl.vertex_array(program, [(vbo, "4f", "in_pos")], ibo)

    def render(self):
        if self.vao:
            self.vao.render()
