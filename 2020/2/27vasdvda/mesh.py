import struct
from functools import partial

import moderngl as mg
import numpy as np
from glm import *
from const import LEFT, RIGHT, BOTTOM, TOP, BACK, FRONT, UP, WIDTH, HEIGHT


def uniform(p, n, v):
    p[n] = v if n in p else None


def mat_to_floats(m):
    for v in m:
        for x in v:
            yield x


def screen_quad():
    p, q = vec4(-1.0, -1.0, 0.0, 1.0), vec4(+1.0, -1.0, 0.0, 1.0)
    s, t = vec4(-1.0, +1.0, 0.0, 1.0), vec4(+1.0, +1.0, 0.0, 1.0)
    return (*p, *q, *s, *t)


def quad_at(i: int, f: vec3, r: vec3, u: vec3):
    v0, v1 = f + r + u, f - r + u
    v2, v3 = f + r - u, f - r - u
    return (
        (*v0, 1.0, *v1, 1.0, *v2, 1.0, *v3, 1.0),
        (i * 4 + 0, i * 4 + 1, i * 4 + 2, i * 4 + 2, i * 4 + 1, i * 4 + 3),
    )


class _RenderObject(object):
    def __init__(self, gl):
        super(_RenderObject, self).__init__()
        self.gl = gl

    def render(self):
        raise NotImplementedError()


class Background(_RenderObject):
    def __init__(self, gl):
        super(Background, self).__init__(gl)

        program = gl.program(
            vertex_shader=open("./gl/background_vs.glsl").read(),
            fragment_shader=open("./gl/background_fs.glsl").read(),
        )
        self.uniform = partial(uniform, program)
        vb = gl.buffer(struct.pack("16f", *screen_quad()))
        ib = gl.buffer(struct.pack("6i", 0, 1, 2, 2, 1, 3))
        self.vertex_array = gl.vertex_array(
            program, [(vb, "4f", "in_pos")], ib, skip_errors=True
        )

    def render(self):
        self.gl.disable(mg.DEPTH_TEST)
        self.vertex_array.render()
        self.gl.enable(mg.DEPTH_TEST)


class Cube(_RenderObject):
    def __init__(self, gl):
        super(Cube, self).__init__(gl)

        program = gl.program(
            vertex_shader=open("./gl/cube_vs.glsl").read(),
            fragment_shader=open("./gl/cube_fs.glsl").read(),
        )
        self.uniform = partial(uniform, program)

        vertices = []
        indices = []

        # face normal, face tangent, face bitangent
        directions = [
            (LEFT, FRONT, TOP),
            (FRONT, RIGHT, TOP),
            (RIGHT, BACK, TOP),
            (BACK, LEFT, TOP),
            (TOP, RIGHT, BACK),
            (BOTTOM, LEFT, FRONT),
        ]

        for i, (f, r, u) in enumerate(directions):
            vrts, inds = quad_at(i, f, r, u)
            vertices.extend(vrts)
            indices.extend(inds)

        vb = gl.buffer(struct.pack(f"{len(vertices)}f", *vertices))
        ib = gl.buffer(np.array(indices, dtype=np.int32))
        self.vertex_array = gl.vertex_array(
            program, [(vb, "4f", "in_pos")], ib, skip_errors=True
        )

        self.fov = 74.0
        self.m = translate(mat4(1.0), vec3(0.0, 0.0, 0.0))
        self.v = lookAt(vec3(0.0, 6.0, 10.0), vec3(0.0), UP)
        self.p = perspective(radians(self.fov), WIDTH / HEIGHT, 0.1, 1000.0)

    def render(self):
        self.m = rotate(self.m, 0.02, UP)
        self.m = rotate(self.m, 0.02, RIGHT)
        self.m = rotate(self.m, 0.02, FRONT)
        self.uniform("mvp", tuple(mat_to_floats(self.p * self.v * self.m)))

        self.gl.enable(mg.DEPTH_TEST)
        self.vertex_array.render()


class SnakeQuads(_RenderObject):
    def __init__(self, gl):
        super(SnakeQuads, self).__init__(gl)

    def render(self):
        1
        # self.gl.enable(mg.DEPTH_TEST)
        # self.vertex_array.render()


class DeferredLight(_RenderObject):
    def __init__(self, gl):
        super(DeferredLight, self).__init__(gl)

        program = gl.program(
            vertex_shader=open("./gl/deferredlight_vs.glsl").read(),
            fragment_shader=open("./gl/deferredlight_fs.glsl").read(),
        )
        self.uniform = partial(uniform, program)
        vb = gl.buffer(struct.pack("16f", *screen_quad()))
        ib = gl.buffer(struct.pack("6i", 0, 1, 2, 2, 1, 3))
        self.vertex_array = gl.vertex_array(
            program, [(vb, "4f", "in_pos")], ib, skip_errors=True
        )

    def render(self):
        1
        # self.gl.disable(mg.DEPTH_TEST)
        # self.vertex_array.render()


if __name__ == "__main__":
    from main import main

    main()
