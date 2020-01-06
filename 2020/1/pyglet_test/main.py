import ctypes as c
import pyglet
import pyglet.gl as gl


def _read(path):
    with open(path, "rb") as f:
        return f.read()


def _compile_shader(vs_src, fs_src):
    vs = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    vs_src_buf = c.create_string_buffer(vs_src)
    c_vs_src = c.cast(c.pointer(vs_src_buf), c.POINTER(c.c_char))
    i = c.c_int32(len(vs_src))
    gl.glShaderSource(vs, 1, c_vs_src, c.byref(i))
    gl.glCompileShader(vs)

    fs = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    fs_src_buf = c.create_string_buffer(fs_src)
    c_fs_src = c.cast(c.pointer(fs_src_buf), c.POINTER(c.c_char))
    i = c.c_int32(len(fs_src))
    gl.glShaderSource(fs, 1, c_fs_src, c.byref(i))
    gl.glCompileShader(fs)

    program = gl.glCreateProgram()
    gl.glAttachShader(program, vs)
    gl.glAttachShader(program, fs)
    gl.glLinkProgram(program)

    gl.glDeleteShader(vs)
    gl.glDeleteShader(fs)

    return program


class PygletWindow(object):
    window = pyglet.window.Window()

    def init():
        PygletWindow.label = pyglet.text.Label(
            "Hello",
            font_name="Ubuntu Light",
            font_size=36,
            x=PygletWindow.window.width // 2,
            y=PygletWindow.window.height // 2,
            anchor_x="center",
            anchor_y="center",
        )

        PygletWindow.initgl()

    @staticmethod
    def initgl():
        vs, fs = _read("./gl/vs.glsl"), _read("./gl/fs.glsl")
        _compile_shader(vs, fs)

    @staticmethod
    @window.event
    def on_draw():
        PygletWindow.window.clear()
        PygletWindow.label.draw()


PygletWindow.init()
pyglet.app.run()
