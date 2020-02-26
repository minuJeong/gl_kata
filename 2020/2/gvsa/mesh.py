import glfw
from glm import *

from const import WIDTH, HEIGHT, UP, RIGHT


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
        GS = open("./gl/gs/calc_normal.glsl").read()

        vb = gl.buffer(reserve=8 * (4 + 4) * 4)
        ib = gl.buffer(reserve=6 * 6 * 4)
        vb.bind_to_storage_buffer(0)
        ib.bind_to_storage_buffer(1)

        self.builder = gl.compute_shader(BUILDER)
        self.updater = gl.compute_shader(UPDATER)
        self.program = gl.program(
            vertex_shader=VS,
            geometry_shader=GS,
            fragment_shader=FS
        )
        self.builder.run(1)

        self.node = gl.vertex_array(
            self.program, [(vb, "4f 4f", "in_pos", "in_normal")], ib, skip_errors=True
        )

        self.m = translate(mat4(1.0), vec3(0.0, 0.0, -6.0))
        self.vp = perspective(radians(74.0), WIDTH / HEIGHT, 0.01, 100.0)

        self.uniform("m", _flatmat(self.m))
        self.uniform("vp", _flatmat(self.vp))

    def uniform(self, uname, uvalue):
        if uname in self.updater:
            self.updater[uname] = uvalue
        if uname in self.program:
            self.program[uname] = uvalue

    def render(self):
        if self.updater:
            self.updater.run(1)

        t = glfw.get_time()

        self.m = rotate(self.m, 0.05, mix(UP, RIGHT, cos(t * 0.5) * 1.5))
        self.uniform("m", _flatmat(self.m))
        self.node.render()


if __name__ == "__main__":
    from main import main
    main()
