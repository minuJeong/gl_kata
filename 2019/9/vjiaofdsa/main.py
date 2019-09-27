import cv2
import pyrealsense2 as pr
import moderngl as mg
import glfw
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Renderer(object):
    def read(self, path):
        with open(path, 'r') as fp:
            return fp.read()

    def recompile(self, t=0.0):
        self.should_recompile = False

        try:
            self.vaos.clear()
            cs = self.GL.compute_shader(self.read("./gl/screen_mesh_compute.glsl"))
            cs.run()

            program = self.GL.program(
                vertex_shader=self.read("./gl/vertex.glsl"),
                fragment_shader=self.read("./gl/fragment.glsl")
            )
            vao = self.GL.vertex_array(program, [(self.vbo, "4f", "in_pos")], self.ibo)

            self.programs.append(program)
            self.vaos.append(vao)
            self.uniform({
                "u_webcam_resolution": (1280, 720),
                "u_rs_color_resolution": (640, 480),
                "u_rs_depth_resolution": (1280, 720),
                "u_screen_resolution": (self.u_width, self.u_height),
            })

            print(f"[{t}] recompiled")

        except Exception as e:
            print(f"RECOMPILE FAILED BECAUSE: {e}")

    def uniform(self, data):
        for p in self.programs:
            for n, v in data.items():
                if n in p:
                    p[n].value = v

    def __init__(self, window, width, height):
        super(Renderer, self).__init__()

        self.window = window
        self.u_width, self.u_height = width, height

        print("initializing realsense..")
        self.pipe = pr.pipeline()
        self.pipe.start()

        print("initializing GPU..")
        self.programs = []
        self.vaos = []

        self.GL = mg.create_context()
        self.vbo = self.GL.buffer(reserve=4 * 4 * 4)
        self.ibo = self.GL.buffer(reserve=6 * 4)
        self.tex3 = self.GL.texture((640, 480), 3, dtype="f1")
        self.tex4 = self.GL.texture((1280, 720), 1, dtype="f2")

        self.vbo.bind_to_storage_buffer(0)
        self.ibo.bind_to_storage_buffer(1)
        self.tex3.use(3)
        self.tex4.use(4)

        self.recompile(0.0)

        self.uniform({
            "u_rs_color_resolution": (640, 480),
            "u_rs_depth_resolution": (1280, 720),
        })

        def on_mod(e):
            self.should_recompile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_mod
        observer = Observer()
        observer.schedule(handler, "./gl")
        observer.start()

    def read_realsense(self):
        try:
            self.frameset = self.pipe.wait_for_frames()

            color = self.frameset.get_color_frame()
            depth = self.frameset.get_depth_frame()

            self.tex3.write(bytes(color.get_data()))
            self.tex4.write(bytes(depth.get_data()))

        except Exception as e:
            print(f"realsense error: {e}")

    def update(self, t):
        if self.should_recompile:
            self.recompile(t)

        self.uniform({"u_time": t})

        self.read_realsense()

        for vao in self.vaos:
            vao.render()

    # GLFW callback
    def on_glfw_resize(self, window, width, height):
        self.u_width, self.u_height = width, height
        self.uniform({"u_screen_resolution": (self.u_width, self.u_height)})
        self.GL.viewport = (0, 0, self.u_width, self.u_height)


def main():
    width, height = 608, 342

    glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(608, 342, "Hello, World", None, None)
    glfw.make_context_current(window)
    context = Renderer(window, width, height)
    glfw.set_window_size_callback(window, context.on_glfw_resize)

    while not glfw.window_should_close(window):

        context.update(glfw.get_time())

        glfw.swap_buffers(window)
        glfw.poll_events()


if __name__ == "__main__":
    main()
