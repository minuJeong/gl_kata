import glfw
import moderngl as mg
import numpy as np
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def init(vao):
    try:
        return gl.vertex_array(
            gl.program(
                vertex_shader=open("./gl/vs.glsl").read(),
                fragment_shader=open("./gl/fs.glsl").read(),
            ), [(gl.buffer(np.array([-1, -1, -1, 1, 1, -1, 1, 1], dtype=np.float32)), "2f", "in_pos")],
            gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32)),
        )
    except Exception as e:
        print(e)
        return vao

width, height = 512, 512
glfw.init()
glfw.window_hint(glfw.FLOATING, glfw.TRUE)
win = glfw.create_window(width, height, "glfw", None, None)
glfw.make_context_current(win)
gl = mg.create_context()
vao = init(None)
recompile = False
def set_recompile(e):
    global recompile
    recompile = True
h = FileSystemEventHandler()
h.on_modified = set_recompile
o = Observer()
o.schedule(h, "./gl/", True)
o.start()
while not glfw.window_should_close(win):
    glfw.poll_events()
    glfw.swap_buffers(win)
    vao.program["u_time"].value = glfw.get_time()
    vao.render()
    if recompile: vao = init(vao)
