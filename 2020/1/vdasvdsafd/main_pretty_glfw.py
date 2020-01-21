import glfw
import moderngl as mg
import numpy as np

glfw.init()
win = glfw.create_window(1024, 1024, "glfw", None, None)
glfw.make_context_current(win)
gl = mg.create_context()
vao = gl.vertex_array(
    gl.program(
        vertex_shader=open("./gl/vs.glsl").read(),
        fragment_shader=open("./gl/fs.glsl").read(),
    ),
    [
        (
            gl.buffer(np.array([-1, -1, -1, 1, 1, -1, 1, 1], dtype=np.float32)),
            "2f",
            "in_pos",
        )
    ],
    gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32)),
)
while not glfw.window_should_close(win):
    glfw.poll_events()
    glfw.swap_buffers(win)
    vao.render()
