_any = any
from glm import *
import moderngl as mg
import numpy as np

from loader import Loader


class Mesh(object):
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

        self.program = gl.program(
            vertex_shader=Loader.load_shader(vertex_shader),
            fragment_shader=Loader.load_shader(fragment_shader),
        )

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

        normal_buffer = gl.buffer(reserve=len(vertex_bytes))
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
        if not self.program and not self.compute:
            return

        binary_sending_types = [mat2, mat3, mat4, vec2, vec3, vec4]
        for p in (self.program, self.compute):
            if not p:
                continue

            for n, v in data.items():
                if n in p:
                    if _any(filter(lambda t: isinstance(v, t), binary_sending_types)):
                        p[n].write(bytes(v))
                    else:
                        p[n].value = v

    def render(self, gl, VP=None):
        if not self.vao:
            self.build_vao(gl)

        VP = VP or mat4(1.0)

        self.update()
        M = self.transform
        MVP = VP * M
        self.uniform({"u_M": M, "u_MVP": MVP})

        self.vao.render()

    def update(self):
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
        vbo = np.hstack((vbo, normal))
        return vbo, ibo

    def build_vao(self, gl, vbo=None, ibo=None):
        if not self.program:
            self.build_material(gl)

        vbo, ibo = self._load_poly(gl)

        idx_nan = np.argwhere(np.isnan(vbo))

        vbo = vbo if isinstance(vbo, mg.Buffer) else gl.buffer(vbo)
        ibo = ibo if isinstance(ibo, mg.Buffer) else gl.buffer(ibo)

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


if __name__ == "__main__":
    gl = mg.create_standalone_context()

    const = gl.buffer(reserve=12)
    const.write(bytes(vec3(512, 512, 24.0)))
    const.bind_to_storage_buffer(24)

    render_target = gl.texture((512, 512), 4)
    fb = gl.framebuffer([render_target])

    screen_mesh = ScreenMesh()
    loaded_mesh = NSightMesh(
        "./mesh/minotaur_head.vbo",
        "./mesh/minotaur_head.ibo",
        "./gl/minotaur_head/vertex.glsl",
        "./gl/minotaur_head/fragment.glsl",
    )

    fb.use()

    screen_mesh.render(gl)

    V = lookAt(vec3(-25.0, 5.0, -25.0), vec3(0.0), vec3(0.0, 1.0, 0.0))
    P = perspective(radians(24.0), 512 / 512, 0.01, 1000.0)
    loaded_mesh.render(gl, V, P)

    img = np.frombuffer(render_target.read(), dtype=np.ubyte).reshape((512, 512, 4))

    import imageio as ii
    ii.imwrite("debug_minotaur_head.png", img)
