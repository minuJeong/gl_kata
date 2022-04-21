import numpy as np


class Mesh(object):
    gl = None
    program = None
    vertex_arrays = []

    def __init__(self, gl, vertex_array=None):
        super().__init__()
        assert gl
        self.gl = gl

        vertex_array = vertex_array or Mesh.get_vertex_array(gl)
        self.set_vertex_arrays([vertex_array])

    def clear_mesh(self):
        self.vertex_arrays = []

    def add_vertex_array(
        self, vertex_array=None, shader=None, vertices_desc=None, indices=None
    ):
        vertex_array = vertex_array or Mesh.get_vertex_array(
            self.gl, shader, vertices_desc, indices
        )
        assert vertex_array

        self.vertex_arrays.append(vertex_array)

    def set_vertex_arrays(self, vertex_arrays):
        self.vertex_arrays = vertex_arrays

    def uniform(self, uname, uvalue):
        for vertex_array in self.vertex_arrays:
            p = vertex_array.program

            if not p or uname not in p:
                continue

            p[uname].value = uvalue

    def render(self):
        for vertex_array in self.vertex_arrays:
            vertex_array.render()

    @staticmethod
    def get_vertices_desc(gl, vertices=None, formats=None, attributes=None):
        vertices = vertices or np.array(
            [
                [-1.0, -1.0, 0.0, 1.0],
                [+1.0, -1.0, 0.0, 1.0],
                [-1.0, +1.0, 0.0, 1.0],
                [+1.0, +1.0, 0.0, 1.0],
            ],
            dtype=np.float32,
        )
        vertices = gl.buffer(vertices) if isinstance(vertices, np.ndarray) else vertices
        formats = formats or "4f"
        attributes = attributes or "in_pos"
        return [[vertices, formats, attributes]]

    @staticmethod
    def get_vertex_array(gl, program=None, vertices_desc=None, indices=None):
        program = program or Mesh.get_program(gl)
        vertices_desc = vertices_desc or Mesh.get_vertices_desc(gl)

        indices = indices or np.array([0, 1, 2, 2, 1, 3], dtype=np.int32)
        indices = gl.buffer(indices) if isinstance(indices, np.ndarray) else indices

        assert program is not None and vertices_desc is not None and indices is not None

        return gl.vertex_array(program, vertices_desc, indices)

    @staticmethod
    def get_program_path(gl, vertex_shader_path, fragment_shader_path):
        return Mesh.get_program(
            gl, open(vertex_shader_path).read(), open(fragment_shader_path).read()
        )

    @staticmethod
    def get_program(gl, vertex_shader=None, fragment_shader=None):
        vertex_shader = (
            vertex_shader
            or """
            #version 460
            in vec4 in_pos;
            out vec4 vs_pos;
            void main(){ vs_pos=in_pos; gl_Position=vs_pos; }
            """
        )
        fragment_shader = (
            fragment_shader
            or """
            #version 460
            in vec4 vs_pos;
            out vec4 fs_color;
            void main(){ fs_color=vec4(0.0, 1.0, 0.5, 1.0); }
            """
        )
        return gl.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)


if __name__ == "__main__":
    from main import main

    main()
