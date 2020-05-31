import struct
from functools import partial

import numpy as np

_all = all
from glm import *
from moderngl.buffer import Buffer


VECTOR_TYPES = (*(vec2, vec3, vec4), *(ivec2, ivec3, ivec4), *(uvec2, uvec3, uvec4))


def _isinstance_all(iterable, types):
    return _all(map(lambda x: isinstance(x, types), iterable))


def _parse_array(data, *args):
    data = data or args
    bytes_data = data

    assert data is not None

    if isinstance(data, Buffer) or isinstance(data, bytes):
        return data

    elif isinstance(data, (list, tuple, set)):
        if _isinstance_all(data, float):
            return struct.pack(f"{len(data)}f", *data)

        elif _isinstance_all(data, int):
            return struct.pack(f"{len(data)}i", *data)

        elif _isinstance_all(data, VECTOR_TYPES):
            serialized_data = tuple([value for vector in data for value in vector])
            return struct.pack(f"{len(serialized_data)}f", *serialized_data)

        else:
            print(f"unsupported type for value in the data: {[type(x) for x in data]}")

    elif isinstance(data, np.ndarray):
        return data.tobytes()

    else:
        print(f"unsupported type for data: {type(data)}")
        return data


class Mesh(object):
    def __init__(self, gl, vspath, fspath):
        super(Mesh, self).__init__()

        self.gl = gl
        self.vspath = vspath
        self.fspath = fspath

        self.compile_shaders()

    def compile_shaders(self):
        try:
            with open(self.vspath) as fp_vs:
                VS = fp_vs.read()

            with open(self.fspath) as fp_fs:
                FS = fp_fs.read()

            self.program = self.gl.program(vertex_shader=VS, fragment_shader=FS)

            print("compiled program")
            return self.program

        except Exception as e:
            print(e)
            return self.program

    def uniform(self, uname, uvalue):
        assert self.program is not None
        if uname not in self.program:
            return

        if isinstance(uvalue, (mat2, mat3, mat4)):
            self.program[uname].write(uvalue)

        self.program[uname] = uvalue

    def render(self):
        raise NotImplementedError


class Quad(Mesh):
    def __init__(self, gl, vspath, fspath):
        quad_vertices = (
            *vec4(-1.0, -1.0, 0.0, 1.0),
            *vec4(-1.0, +1.0, 0.0, 1.0),
            *vec4(+1.0, -1.0, 0.0, 1.0),
            *vec4(+1.0, +1.0, 0.0, 1.0),
        )
        self.vertices = gl.buffer(np.array(quad_vertices, dtype=np.float32))
        self.indices = gl.buffer(np.array((0, 1, 2, 2, 1, 3), dtype=np.int32))
        super(Quad, self).__init__(gl, vspath, fspath)

    def compile_shaders(self):
        super(Quad, self).compile_shaders()
        self.vetex_array = self.gl.vertex_array(
            self.program, [(self.vertices, "4f", "in_pos")], self.indices
        )

    def render(self):
        self.vetex_array.render()


if __name__ == "__main__":
    from main import main

    main()
