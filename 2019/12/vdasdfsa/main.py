from glm import *
import glfw
import numpy as np
import moderngl as mg
import imageio as ii
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def read(path):
    with open(path, "r") as fp:
        return fp.read()


class Client(object):
    def __init__(self, window):
        super(Client, self).__init__()

        self.window = window
        self.width, self.height = glfw.get_window_size(window)

        self.gl = mg.create_context()
        self.compile()

        def on_modified(e):
            self.should_compile = True

        h = FileSystemEventHandler()
        h.on_modified = on_modified
        o = Observer()
        o.schedule(h, "./gl/", True)
        o.start()

        glfw.set_key_callback(window, self.on_key)

    def on_key(self, window, code, key, act, mod):
        if code == glfw.KEY_SPACE:
            if act == glfw.RELEASE:
                self.capture_buffer("gbuffer.png", self.gbuffer.read(components=4))
                self.capture_buffer(
                    "pprenderbuffer_0.png", self.pprenderbuffer_0.read(components=4)
                )
                self.capture_buffer(
                    "pprenderbuffer_1.png", self.pprenderbuffer_1.read(components=4)
                )
                print("captured buffers")

    def capture_buffer(self, path, bufferdata):
        img = np.frombuffer(bufferdata, dtype=np.ubyte).reshape(
            (self.height, self.width, 4)
        )
        ii.imwrite(path, img)

    def compile(self):
        self.should_compile = False

        try:
            NUM_QUAD = 5
            indices = []
            for i in range(NUM_QUAD):
                ofs = i * 4
                indices.extend([0 + ofs, 1 + ofs, 2 + ofs, 2 + ofs, 1 + ofs, 3 + ofs])

            # compute shader
            CS = read("./gl/mesh.cs")
            self.cs = self.gl.compute_shader(CS)

            # generate vb/ib
            screen_vb = self.gl.buffer(
                np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype=np.float32)
            )
            screen_ib = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], np.int32))
            self.group = NUM_QUAD, 1

            # background quad
            VS, FS = read("./gl/screen.vs"), read("./gl/background.fs")
            bgprogram = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            self.bgvao = self.gl.vertex_array(bgprogram, [(screen_vb, "2f", "in_pos")], screen_ib)

            # particle vao
            VS, FS = read("./gl/quad.vs"), read("./gl/quad.fs")
            program = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            vb = self.gl.buffer(reserve=(4 + 4 + 4) * 4 * NUM_QUAD * 4)
            vb.bind_to_storage_buffer(0)

            # compile particle quads
            self.particles = self.gl.vertex_array(
                program,
                [(vb, "4f 4f 4f", "in_pos", "in_uv", "in_color")],
                self.gl.buffer(np.array(indices, dtype=np.int32)),
                skip_errors=True,
            )

            # screen shaders
            VS, FS = read("./gl/screen.vs"), read("./gl/screen_bloomblur.fs")
            screen_bloomblur_program = self.gl.program(
                vertex_shader=VS, fragment_shader=FS
            )
            VS, FS = read("./gl/screen.vs"), read("./gl/screen_final.fs")
            screen_final_program = self.gl.program(vertex_shader=VS, fragment_shader=FS)

            # screen vetex arrays
            self.screen_bloomblur = self.gl.vertex_array(
                screen_bloomblur_program, [(screen_vb, "2f", "in_pos")], screen_ib
            )
            self.screen_final = self.gl.vertex_array(
                screen_final_program, [(screen_vb, "2f", "in_pos")], screen_ib
            )

            # gbuffer
            self.gbuf_basecolor = self.gl.texture((self.width, self.height), 4, dtype="f4")
            self.gbuf_basecolor.repeat_x = False
            self.gbuf_basecolor.repeat_y = False

            self.gbuffer = self.gl.framebuffer([self.gbuf_basecolor])

            # bloom buffer
            self.bloomtex = self.gl.texture((self.width, self.height), 4, dtype="f4")
            self.postprocessframe = self.gl.framebuffer([self.bloomtex])

            # uniforms
            u_aspect = self.width / self.height
            self.uniform(self.cs, "u_aspect", u_aspect)
            self.uniform(program, "u_aspect", u_aspect)
            self.uniform(screen_final_program, "u_aspect", u_aspect)
            self.uniform(
                screen_bloomblur_program, "u_res", vec2(self.width, self.height)
            )
            self.uniform(screen_bloomblur_program, "u_source", 0)
            self.uniform(screen_final_program, "u_gbuffer_basecolor", 0)
            self.uniform(screen_final_program, "u_bloomtex", 1)

            print("done")

        except Exception as e:
            print(e)

    def uniform(self, p, n, v):
        if n not in p:
            return

        if isinstance(v, (float, int, bool)):
            p[n].value = v

        else:
            p[n].write(bytes(v))

    def clear(self):
        self.gl.clear()
        self.gbuffer.clear()

    def push_utime(self):
        u_time = glfw.get_time()
        self.uniform(self.cs, "u_time", u_time)
        self.uniform(self.bgvao.program, "u_time", u_time)
        self.uniform(self.particles.program, "u_time", u_time)
        self.uniform(self.screen_final.program, "u_time", u_time)

    def advance_particles(self):
        self.cs.run(*self.group)

    def render_background(self):
        self.bgvao.render()

    def render_particles(self):
        self.particles.render()

    def bloom(self):
        self.gbuf_basecolor.use(0)
        self.screen_bloomblur.render()

    def finalrender(self):
        self.gbuf_basecolor.use(0)
        self.bloomtex.use(1)
        self.screen_final.render()

    def update(self):
        if self.should_compile:
            self.compile()
            return

        self.clear()
        self.push_utime()
        self.advance_particles()

        self.gbuffer.use()
        self.render_background()

        self.gl.enable(mg.BLEND)
        self.render_particles()

        self.postprocessframe.use()
        self.bloom()

        self.gl.screen.use()
        self.finalrender()


def main():
    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(1920, 1280, "'-^/", None, None)
    glfw.make_context_current(window)
    client = Client(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
        client.update()


if __name__ == "__main__":
    main()
