from glm import *
import moderngl as mg
import numpy as np
import imageio as ii


WIDTH, HEIGHT = 512, 512
COUNT_CUBES = 128
UP = vec3(0.0, 1.0, 0.0)

cs_src = open("./gl/cs_build_cube.glsl").read()

gl = mg.create_context(standalone=True)
cs = gl.compute_shader(cs_src)
cubes_buffer = gl.buffer(reserve=COUNT_CUBES * 13 * 4)
cubes_buffer.bind_to_storage_buffer(0)
ib = gl.buffer(reserve=COUNT_CUBES * 36)

cs.run(COUNT_CUBES // 8 + 1)

gbuffer_colour = gl.texture((WIDTH, HEIGHT), 4)
gbuffer = gl.framebuffer([gbuffer_colour])

vs_src = open("./gl/debug/render_vs.glsl").read()
fs_src = open("./gl/debug/render_fs.glsl").read()
program = gl.program(vertex_shader=vs_src, fragment_shader=fs_src)
va = gl.vertex_array(program, [(cubes_buffer, "4f 4f 4f", "in_pos", "in_texcoord", "in_normal")], ib, skip_errors=True)

if "u_MVP" in program:
    V = lookAt(vec3(-2.0, 10.0, -10.0), vec3(0.0), UP)
    aspect = 1.0
    near, far = 0.01, 100.0
    P = perspective(radians(74.0), aspect, near, far)
    program["u_MVP"].write(bytes(P * V))

gbuffer.use()
gl.point_size = 20.0
va.render(mode=mg.POINTS)

img = np.frombuffer(gbuffer_colour.read(), dtype=np.ubyte).reshape((WIDTH, HEIGHT, 4))
ii.imwrite("./output.png", img)
