
class MeshDef(object):
    vertex_shader = None
    fragment_shader = None
    vertices = None
    indices = None

    def __init__(self, vertex_shader, fragment_shader, vertices, indices):
        self.vertex_shader = vertex_shader
        self.fragment_shader = fragment_shader
        self.vertices = vertices
        self.indices = indices


class Mesh(object):
    def __init__(self, gl, mesh_def):
        super(Mesh, self).__init__()

        VS, FS = (
            open(mesh_def.vertex_shader).read(),
            open(mesh_def.fragment_shader).read(),
        )
        self.program = gl.program(vertex_shader=VS, fragment_shader=FS)
        vb = gl.buffer(mesh_def.vertices)
        ib = gl.buffer(mesh_def.indices)
        self.render = gl.vertex_array(self.program, [(vb, "4f", "in_pos")], ib).render

    def uniform(self, uname, uvalue):
        if uname in self.program:
            self.program[uname] = uvalue


if __name__ == "__main__":
    from main import main
    main()
