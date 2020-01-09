_any = any
from glm import *
import moderngl as mg
import numpy as np

from loader import Loader


class Mesh(object):
    programs_cache = {}

    def __init__(self, transform=None):
        super(Mesh, self).__init__()
        self.transform = transform or mat4(1.0)
        self.vao = None
        self.compute = None
        self.program = None
        self.vertex_shader = None
        self.fragment_shader = None

    def set_transform(self, transform):
        self.transform = transform

    def set_technique(self, vertex_shader=None, fragment_shader=None):
        vertex_shader = vertex_shader or "./gl/minotaur/vertex.glsl"
        fragment_shader = fragment_shader or "./gl/minotaur/fragment.glsl"
        self.vertex_shader, self.fragment_shader = vertex_shader, fragment_shader

    def build_material(self, gl, vertex_shader=None, fragment_shader=None):
        vertex_shader = vertex_shader or self.vertex_shader
        fragment_shader = fragment_shader or self.fragment_shader

        assert vertex_shader and fragment_shader, self

        vssrc = Loader.load_shader(vertex_shader)
        fssrc = Loader.load_shader(fragment_shader)

        cachekey = (vssrc, fssrc)
        if cachekey in Mesh.programs_cache:
            self.program = Mesh.programs_cache[cachekey]

        else:
            self.program = gl.program(
                vertex_shader=vssrc,
                fragment_shader=fssrc,
            )
            Mesh.programs_cache[cachekey] = self.program

        self.build_vao(gl)

    def compute_normal(self, gl, vbo, ibo):
        vertex_shape = vbo.shape
        vertex_bytes = vbo.tobytes()

        len_ibo = len(ibo)
        len_tris = len_ibo // 3

        ibo = ibo.reshape((-1, 3))
        tri_ids = np.arange(0, len_tris).reshape((-1, 1))
        tris = np.hstack((tri_ids, ibo))

        gl.buffer(vertex_bytes).bind_to_storage_buffer(4)
        gl.buffer(tris.tobytes()).bind_to_storage_buffer(5)

        num_verts = len(vertex_bytes) // 16  # 4 components * 4 bytes
        normals = np.array([0.5, 0.5, 1.0, 1.0] * num_verts, dtype=np.float32)
        normal_buffer = gl.buffer(normals)
        normal_buffer.bind_to_storage_buffer(6)

        self.compute = gl.compute_shader(
            Loader.load_shader("./gl/compute/compute_vertex_normal.glsl")
        )
        self.uniform({"u_tris_count": len_ibo // 3})
        self.compute.run(int(floor(len_ibo / 32)))

        return np.frombuffer(normal_buffer.read(), dtype=np.float32).reshape(
            vertex_shape
        )

    def build_vao(self, gl, vertices, indices):
        if not self.program:
            self.build_material(gl)

        vbo = vertices if isinstance(vertices, mg.Buffer) else gl.buffer(vertices)
        ibo = indices if isinstance(indices, mg.Buffer) else gl.buffer(indices)
        self.compute_normal(gl, vbo, ibo)
        self.vao = gl.vertex_array(
            self.program,
            [(vbo, "3f 3f", "in_pos", "in_computed_normal")],
            ibo,
            skip_errors=True,
        )

    def uniform(self, data):
        binary_sending_types = (mat2, mat3, mat4, vec2, vec3, vec4)
        for p in (self.program, self.compute):
            if not p:
                continue

            for n, v in data.items():
                if n not in p:
                    continue

                if isinstance(v, binary_sending_types):
                    p[n].write(bytes(v))
                elif isinstance(v, (int, float)):
                    p[n].value = v
                else:
                    raise Exception("Unsupported")

    def render(self, gl, MVP=None, VP=None):
        if not self.vao:
            self.build_vao(gl)

        M = self.transform
        if MVP is None:
            VP = VP or mat4(1.0)
            MVP = VP * M

        self.uniform({"u_M": M, "u_MVP": MVP})
        self.vao.render()
        self.update()

    def update(self):
        """ override this method to perform update on your own """
        pass


class NSightMesh(Mesh):
    def __init__(self, vbo_path, ibo_path, technique_vs, technique_fs):
        super(NSightMesh, self).__init__()
        self.vbo_path = vbo_path
        self.ibo_path = ibo_path
        self.set_technique(technique_vs, technique_fs)

    def _load_poly(self, gl):
        vbo = Loader.load_vbo(self.vbo_path)
        ibo = Loader.load_ibo(self.ibo_path)

        normal = self.compute_normal(gl, vbo[:, 0:4], ibo)[:, 0:3]
        normal = np.nan_to_num(normal)
        vbo = np.hstack((vbo, normal))
        return vbo, ibo

    def build_vao(self, gl):
        if not self.program:
            self.build_material(gl)

        vbo, ibo = self._load_poly(gl)
        vbo = gl.buffer(vbo.tobytes())
        ibo = gl.buffer(ibo.tobytes())

        self.vao = gl.vertex_array(
            self.program,
            [
                (
                    vbo,
                    " ".join([f"{x}f" for x in [3, 4, 4, 4, 2, *[4] * 10, 3]]),
                    *[f"in_pos_{x}" for x in range(7)],
                    *[f"in_texcoord_{x}" for x in range(8)],
                    "in_computed_normal",
                )
            ],
            ibo,
            skip_errors=True,
        )


class Quad(Mesh):
    def __init__(self, x, y, w, h):
        super(Quad, self).__init__()
        self.x, self.y, self.w, self.h = x, y, w, h
        self.set_technique("./gl/quad_vs.glsl", "./gl/quad_fs.glsl")

    def build_vao(self, gl, vertices=None, indices=None):
        if vertices or indices:
            raise Exception("Quad doesn't accept vertices nor indices")

        if not self.program:
            self.build_material(gl)

        x, y, w, h = self.x, self.y, self.w, self.h
        vbo = gl.buffer(
            np.array([x, y, x, y + h, x + w, y, x + w, y + h])
            .astype(np.float32)
            .tobytes()
        )
        ibo = gl.buffer(np.array([0, 1, 2, 2, 1, 3]).astype(np.int32).tobytes())

        self.vao = gl.vertex_array(
            self.program, [(vbo, "2f", "in_pos")], ibo, skip_errors=True
        )


class ScreenMesh(Quad):
    def __init__(self, vs, fs):
        super(ScreenMesh, self).__init__(-1.0, -1.0, 2.0, 2.0)
        self.set_technique(vs, fs)
        V = mat4(1.0)
        P = ortho(0.0, +1.0, +1.0, 0.0, -1.0, +1.0)
        self.VP = P * V

    def render(self, gl, VP=None):
        super(ScreenMesh, self).render(gl, self.VP)
