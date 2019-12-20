import numpy as np
import moderngl as mg
import imageio as ii


def read(path, mode):
    with open(path, mode) as fp:
        return fp.read()


gl = mg.create_standalone_context()
vs, fs = read("./gl/quad.vs", "r"), read("./gl/quad.fs", "r")
vb, ib = read("./mesh/quad.vb", "rb"), read("./mesh/quad.ib", "rb")
vb, ib = gl.buffer(vb), gl.buffer(ib)
program = gl.program(vertex_shader=vs, fragment_shader=fs)
vao = gl.vertex_array(program, [(vb, "2f", "in_pos")], ib)

color = gl.texture((512, 512), 4)
fbo = gl.framebuffer([color])

fbo.use()
vao.render()

img = np.frombuffer(color.read(), dtype=np.ubyte).reshape((512, 512, 4))
img = img[::-1]
ii.imwrite("output.png", img)
