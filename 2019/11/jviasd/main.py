import moderngl as mg
import numpy as np
import glfw
from glm import *


def readfile(path):
    with open(path, "r") as fp:
        return fp.read()


def box(gl):
    points = np.zeros(shape=(8, 3)).astype(np.float32)
    i = 0
    for z in [-1.0, +1.0]:
        for y in [-1.0, +1.0]:
            for x in [-1.0, +1.0]:
                points[i] = x, y, z
                i += 1

    indices = [
        [0, 2, 1],
        [2, 3, 1],
        [4, 5, 6],
        [6, 5, 7],
        [1, 7, 5],
        [7, 1, 3],
        [0, 6, 2],
        [6, 0, 4],
        [2, 7, 3],
        [7, 2, 6],
    ]

    normals = np.zeros(shape=(8, 3)).astype(np.float32)
    i = 0
    for uvw in indices:
        u, v, w = uvw
        uu = vec3(*points[u])
        vv = vec3(*points[v])
        ww = vec3(*points[w])
        n = cross(vv - uu, ww - uu)
        normals[u] = n.x, n.y, n.z
        i += 1

    points = np.hstack((points, normals))

    vbo = gl.buffer(points.tobytes())
    ibo = gl.buffer(np.array(indices).astype(np.int32).tobytes())
    return vbo, ibo


def uniform(p, n, v):
    BIN_TYPES = (
        [vec2, vec3, vec4]
        + [ivec2, ivec3, ivec4]
        + [uvec2, uvec3, uvec4]
        + [mat2, mat3, mat4]
    )

    if n in p:
        if isinstance(v, tuple(BIN_TYPES)):
            p[n].write(bytes(v))
        else:
            p[n].value = v


def main():
    glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(512, 512, "title", None, None)
    glfw.make_context_current(window)

    gl = mg.create_context()
    gl.enable(mg.CULL_FACE)

    p = gl.program(
        vertex_shader=readfile("./gl/vs_aaa.glsl"),
        fragment_shader=readfile("./gl/fs_aaa.glsl"),
    )
    v, i = box(gl)
    va = gl.vertex_array(
        p, [(v, "3f 3f", "in_pos", "in_normal")], i, skip_errors=True
    )

    while not glfw.window_should_close(window):
        gl.clear()

        t = glfw.get_time()

        M = translate(mat4(1.0), vec3(0.0, 0.0, 0.0))
        V = lookAt(
            vec3(cos(t * 2.0) * 2.0, 2.0, sin(t * 2.0) * 2.0),
            vec3(0.0),
            vec3(0.0, 1.0, 0.0),
        )
        P = perspective(radians(94.0), 1.0, 0.01, 100.0)
        MVP = P * V * M

        uniform(p, "u_MVP", MVP)
        va.render()
        glfw.poll_events()
        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
