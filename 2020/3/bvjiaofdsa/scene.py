import struct
from functools import partial

from glm import *

from transform import Transform
from camera import Camera
from const import _uniform, mat_to_16f


class RenderObj(object):
    def __init__(self, gl):
        super(RenderObj, self).__init__()
        self.gl = gl
        self.model = Transform()


class Quad(RenderObj):
    def __init__(self, gl, program):
        super(Quad, self).__init__(gl)

        p, q = vec4(-1.0, -1.0, 0.0, 1.0), vec4(1.0, -1.0, 0.0, 1.0)
        r, t = vec4(-1.0, 1.0, 0.0, 1.0), vec4(1.0, 1.0, 0.0, 1.0)
        vertices = struct.pack(f"{4 * 4}f", *(*p, *q, *r, *t))
        indices = struct.pack("6i", *(0, 1, 2, 2, 1, 3))
        vertex_buffer = self.gl.buffer(vertices)
        index_buffer = self.gl.buffer(indices)
        self.render = self.gl.vertex_array(
            program, [(vertex_buffer, "4f", "in_pos")], index_buffer, skip_errors=True
        ).render
        self.uniform = partial(_uniform, program)


class Scene(object):
    def __init__(self, gl):
        super(Scene, self).__init__()
        self.gl = gl

    def init(self):
        self.nodes = []
        self.camera = Camera()

        VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
        quad_program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
        self.nodes.append(Quad(self.gl, quad_program))

    def render(self):
        VP = self.camera.get_mat()
        for node in self.nodes:
            M = node.model.get_mat()
            MVP = VP * M
            node.uniform("u_model", mat_to_16f(M))
            node.uniform("u_mvp", mat_to_16f(MVP))

            print("----")
            print(MVP)
            print("====")
            node.render()


if __name__ == "__main__":
    from main import main
    main()
