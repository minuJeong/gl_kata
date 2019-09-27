"""
requirements
- numpy
- moderngl
- glm
- imageio
"""

from itertools import chain

import numpy as np
import moderngl as mg
import glm
import imageio as ii


def _read(path):
    context = None
    with open(path, 'r') as fp:
        context = fp.read()

    output = []
    for line in context.splitlines():
        if line.startswith("#include "):
            output.append(_read("#include ".join(line.split("#include ")[1:])))
            continue

        output.append(line)

    return "\n".join(output)


def _uniform(p, data):
    for n, v in data.items():
        if n in p:
            p[n].value = v


gl = mg.create_standalone_context()

u_width, u_height = 512, 512
render_texture = gl.texture((u_width, u_height), 4, dtype="f4")
framebuffer = gl.framebuffer((render_texture))
scope = gl.scope(framebuffer)

cs = _read("./gl/cs.glsl")
cs = gl.compute_shader(cs)

# vbo = np.array([
#     [0,  1.0, 1.0, 0.0,  0.0, 0.0, 0.5, ],
#     [1,  0.0, 1.0, 0.0,  0.0, 0.0, 0.5, ],
#     [2,  0.0, 1.0, 1.0,  0.0, 0.0, 0.5, ],
#     [3,  1.0, 1.0, 1.0,  0.0, 0.0, 0.5, ],
#     [4,  1.0, 0.0, 0.0,  0.0, 0.0, 0.5, ],
#     [5,  0.0, 0.0, 0.0,  0.0, 0.0, 0.5, ],
#     [6,  0.0, 0.0, 1.0,  0.0, 0.0, 0.5, ],
#     [7,  1.0, 0.0, 1.0,  0.0, 0.0, 0.5, ],
# ])

vbo = np.array([
    [0,  1.0, 1.0, 0.0,  0.0, 0.0, 0.5, ],
    [1,  0.0, 1.0, 0.0,  0.0, 0.0, 0.5, ],
    [2,  0.0, 1.0, 0.0,  0.0, 0.0, 0.5, ],
    [3,  1.0, 1.0, 1.0,  0.0, 0.0, 0.5, ],
])
LEN_VERTICES = len(vbo)

vbo[:, 0] = np.arange(len(vbo))
vbo = vbo.astype(np.float32).tobytes()
vbo = gl.buffer(vbo)
vbo.bind_to_storage_buffer(0)

# ibo = np.array([
#     0, 2, 1,  2, 0, 3,
#     0, 5, 1,  5, 0, 4,
#     5, 4, 6,  6, 4, 7,
#     0, 4, 3,  3, 4, 7,
#     2, 3, 6,  6, 3, 7,
#     2, 1, 5,  2, 5, 6,
# ])

ibo = np.array([
    0, 1, 2,  2, 1, 3,
])
LEN_FACES = len(ibo) / 3

ibo = ibo.astype(np.int32).tobytes()
ibo = gl.buffer(ibo)
ibo.bind_to_storage_buffer(1)

vs, fs = _read("./gl/vs.glsl"), _read("./gl/fs.glsl")

program = gl.program(
    vertex_shader=vs,
    fragment_shader=fs
)

vao = gl.vertex_array(program, [(vbo, "1u 3f 3f", "in_index", "in_pos", "in_normal")], ibo, skip_errors=True)

M = glm.mat4()
V = glm.translate(glm.mat4(), glm.vec3(0.0, 0.0, -10.0))
P = glm.perspective(45.0, u_width / u_height, 0.1, 100.0)
u_MVP = P * V * M

print(u_MVP)

uniform_data = {
    "u_width": u_width,
    "u_height": u_height,
    "u_MVP": tuple(chain.from_iterable(u_MVP))
}
_uniform(program, uniform_data)

gx = int(LEN_VERTICES / 8)
gy, gz = 1, 1
with scope:
    cs.run(gx, gy, gz)
    vao.render()

rendered = np.frombuffer(render_texture.read(), dtype=np.float32)
rendered = rendered.reshape((u_height, u_width, 4))
rendered = np.multiply(rendered, 255.0)
rendered = rendered.astype(np.uint8)
ii.imwrite("output.png", rendered)
