import moderngl as mg
import numpy as np
import imageio as ii
gl = mg.create_standalone_context()
colortex = gl.texture((1024, 1024), 4, dtype="f4")
gl.framebuffer([colortex]).use()
gl.vertex_array(gl.program(vertex_shader=open("./gl/vs.glsl").read(), fragment_shader=open("./gl/fs.glsl").read()), [(gl.buffer(np.array([-1, -1, -1, 1, 1, -1, 1, 1], dtype=np.float32)), "2f", "in_pos", )], gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))).render()
ii.imwrite("output.png", np.multiply(np.frombuffer(colortex.read(), dtype=np.float32), 255.0).astype(np.uint8).reshape((1024, 1024, 4))[::-1])
