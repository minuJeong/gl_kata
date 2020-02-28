import numpy as np
from glm import *


class RenderObject(object):
    def __init__(self):
        super(RenderObject, self).__init__()
        self.programs = []

    def uniform(self, uname, uvalue):
        for p in self.programs:
            if uname in p:
                p[uname] = uvalue


class BackgroundMesh(RenderObject):
    def __init__(self, gl):
        super(BackgroundMesh, self).__init__()

        VS, FS = open("./gl/vs.glsl").read(), open("./gl/fs.glsl").read()
        P = gl.program(vertex_shader=VS, fragment_shader=FS)

        p, q = vec4(-1.0, -1.0, 0.0, 1.0), vec4(+1.0, -1.0, 0.0, 1.0)
        s, t = vec4(-1.0, +1.0, 0.0, 1.0), vec4(+1.0, +1.0, 0.0, 1.0)
        vertices = gl.buffer(np.array((*p, *q, *s, *t), dtype=np.float32))
        content = [(vertices, "4f", "in_pos")]
        indices = gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))
        self.render = gl.vertex_array(P, content, indices).render

        self.programs.append(P)


if __name__ == "__main__":
    from main import main
    main()
