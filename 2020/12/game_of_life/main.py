import glfw
import moderngl as mg
import numpy as np
import imageio as ii
from glm import vec4, vec2, ivec2
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


RENDER_RESOLUTION = 1024
BUFFER_RESOLUTION = 256


class Client(object):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.gl = mg.create_context(require=460)
        self.compile()

        def on_mod(e):
            self._need_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_mod
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

        self.is_drag = 0
        self.pos = ivec2(0, 0)
        self._should_capture_buffers = False

        glfw.set_cursor_pos_callback(window, self.on_cursor_pos)
        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_key_callback(window, self.on_key)

    def _winpos_to_bufpos(self, x, y):
        x = min(max(x, 0), RENDER_RESOLUTION)
        y = min(max(y, 0), RENDER_RESOLUTION)
        pos = vec2(x, RENDER_RESOLUTION - y)
        pos /= RENDER_RESOLUTION
        pos *= BUFFER_RESOLUTION * 2.0
        return ivec2(pos)

    def on_cursor_pos(self, window, x, y):
        if not self.is_drag == 1:
            return

        self.pos = self._winpos_to_bufpos(x, y)

    def on_mouse_button(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                self.pos = self._winpos_to_bufpos(*glfw.get_cursor_pos(window))
                self.is_drag = 1
            else:
                self.is_drag = 0

        elif button == glfw.MOUSE_BUTTON_RIGHT:
            if action == glfw.RELEASE:
                self._need_compile = True

    def on_key(self, window, key, scancode, action, mods):
        if key == glfw.KEY_SPACE and action == glfw.RELEASE:
            self._should_capture_buffers = True

    def compile(self):
        self._need_compile = False

        try:
            CS = open("./gl/game_of_life.cs").read()
            self.cs = self.gl.compute_shader(CS)

            b0 = self.gl.buffer(reserve=BUFFER_RESOLUTION * BUFFER_RESOLUTION * (4 + 4) * 4)
            b1 = self.gl.buffer(reserve=BUFFER_RESOLUTION * BUFFER_RESOLUTION * (4 + 4) * 4)
            b0.bind_to_storage_buffer(0)
            b1.bind_to_storage_buffer(1)

            self.i = 0
            self.buffers = [b0, b1]

            VS, FS = open("./gl/quad.vs").read(), open("./gl/quad.fs").read()
            p = self.gl.program(vertex_shader=VS, fragment_shader=FS)
            v = self.gl.buffer(
                np.array(
                    [
                        *vec4(-1.0, -1.0, 0.0, 1.0),
                        *vec4(+1.0, -1.0, 0.0, 1.0),
                        *vec4(-1.0, +1.0, 0.0, 1.0),
                        *vec4(+1.0, +1.0, 0.0, 1.0),
                    ],
                    dtype=np.float32,
                )
            )
            i = self.gl.buffer(np.array([0, 1, 2, 2, 1, 3], dtype=np.int32))
            self.quad = self.gl.vertex_array(p, [(v, "4f", "in_pos")], i)

            self.uniform("u_map_size", BUFFER_RESOLUTION)

            print("compiled")

        except Exception as e:
            print(e)

    def capture_buffers(self):
        self._should_capture_buffers = False

        for i, b in enumerate(self.buffers):
            data = np.frombuffer(b.read(), dtype=np.float32)
            data = data.reshape((BUFFER_RESOLUTION, BUFFER_RESOLUTION, (4 + 4)))

            is_alive_xyzw = np.multiply(data[:, :, 0:4], 255.0).astype(np.uint8)
            rgba = np.multiply(data[:, :, 4:8], 255.0).astype(np.uint8)

            ii.imwrite(f"buffer_capture_is_alive_{i}.png", is_alive_xyzw)
            ii.imwrite(f"buffer_capture_rgba_{i}.png", rgba)

        print("captured buffers")

    def uniform(self, uname, uvalue):
        if self.quad is None:
            return

        ps = [self.quad.program, self.cs]
        for p in ps:
            if uname not in p:
                continue

            if isinstance(uvalue, ivec2):
                p[uname].write(uvalue)
            else:
                p[uname] = uvalue

    def update(self):
        if self._need_compile:
            self.compile()
            return

        t = glfw.get_time()
        self.uniform("u_time", t)
        self.uniform("u_pos", self.pos / 2)
        self.uniform("u_is_drag", self.is_drag)

        self.cs.run(BUFFER_RESOLUTION // 8, BUFFER_RESOLUTION // 8)

        if self._should_capture_buffers:
            self.capture_buffers()

        if self.i == 0:
            self.i = 1
            self.buffers[0].bind_to_storage_buffer(1)
            self.buffers[1].bind_to_storage_buffer(0)
        else:
            self.i = 0
            self.buffers[0].bind_to_storage_buffer(0)
            self.buffers[1].bind_to_storage_buffer(1)

        self.quad.render()


def main():
    assert glfw.init()

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(RENDER_RESOLUTION, RENDER_RESOLUTION, "", None, None)
    glfw.make_context_current(window)

    client = Client(window)

    while not glfw.window_should_close(window):
        glfw.swap_buffers(window)
        glfw.poll_events()
        client.update()


if __name__ == "__main__":
    main()
