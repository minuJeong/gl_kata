import moderngl as mg


def read_file(path):
    with open(path, "r") as fp:
        return fp.read()


def main():
    gl = mg.create_standalone_context()

    vbo = gl.buffer(reserve=8 * 4 * 4)
    ibo = gl.buffer(reserve=6 * 2 * 4)

    vbo.bind_to_storage_buffer(0)
    ibo.bind_to_storage_buffer(1)

    cs = gl.compute_shader(read_file("./gl/build_cube.compute.glsl"))
    cs.run(1)
