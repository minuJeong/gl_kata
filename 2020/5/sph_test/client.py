import math
from functools import partial

import glfw
import imgui
import numpy as np
import moderngl as mg
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from integrations.imgui import ModernGLGLFWRenderer


NUM_PARTICLES = 32 * 32 * 32
NUM_THREADS_PER_GROUP = 64

NUM_GRID = 12 * 12 * 12
GRID_CS_GROUP_SIZE_X = math.ceil(NUM_GRID / NUM_THREADS_PER_GROUP)


class SimulateStage(object):
    def __init__(self, gl, source):
        super().__init__()
        self.gl = gl

        with open(source, "r") as fp:
            self.source = fp.read()
        self.process = self.gl.compute_shader(self.source)

    def uniform(self, uname, uvalue):
        if uname not in self.process:
            return

        if isinstance(uvalue, (mat2, mat3, mat4)):
            self.process[uname].write(uvalue)

        elif isinstance(
            uvalue, (vec2, vec3, vec4, uvec2, uvec3, uvec4, ivec2, ivec3, ivec4)
        ):
            self.process[uname].write(uvalue)
        else:
            self.process[uname] = uvalue

    def run(self, gx=1, gy=1, gz=1):
        gx = NUM_PARTICLES // 64
        gy = NUM_PARTICLES // 64
        gz = 1
        self.process.run(gx, gy, gz)


class StorageBuffer(object):
    def __init__(self, gl):
        super().__init__()
        self.gl = gl


class InjectStage(SimulateStage):
    def __init__(self, gl):
        super().__init__(gl, "./gl/cs_0_inject.glsl")

    def run(self, gx=1, gy=1, gz=1):
        gx = NUM_PARTICLES // 64
        gy = NUM_PARTICLES // 64
        gz = NUM_PARTICLES // 64
        super().run(gx, gy, gz)


class AdvectStage(SimulateStage):
    def __init__(self, gl):
        super().__init__(gl, "./gl/cs_1_advect.glsl")

    def run(self):
        gx = NUM_PARTICLES // 64
        gy = NUM_PARTICLES // 64
        gz = NUM_PARTICLES // 64
        super().run(gx, gy, gz)


class PressureStage(SimulateStage):
    def __init__(self, gl):
        super().__init__(gl, "./gl/cs_2_pressure.glsl")

    def run(self):
        gx = NUM_PARTICLES // 64
        gy = NUM_PARTICLES // 64
        gz = NUM_PARTICLES // 64
        super().run(gx, gy, gz)


class VorticityStage(SimulateStage):
    def __init__(self, gl):
        super().__init__(gl, "./gl/cs_3_vorticity.glsl")


class EvolveStage(SimulateStage):
    def __init__(self, gl):
        super().__init__(gl, "./gl/cs_4_evolve.glsl")


class VelocityBuffer(StorageBuffer):
    def __init__(self, gl):
        super().__init__(gl)


class ParticlesBuffer(StorageBuffer):
    BIND_CHANNEL = 0

    def __init__(self, gl):
        super().__init__(gl)

        # position
        # velocity
        # texcoord0
        buffer_size = (4 + 4 + 4) * NUM_PARTICLES
        self.buffer = self.gl.buffer(reserve=buffer_size)
        self.buffer.bind_to_storage_buffer(ParticlesBuffer.BIND_CHANNEL)


class GridBuffer(StorageBuffer):
    BIND_CHANNEL = 1

    def __init__(self, gl):
        super().__init__(gl)

        # vec4 velosity
        # float density
        buffer_size = (4 + 1) * NUM_GRID
        self.buffer = self.gl.buffer(reserve=buffer_size)
        self.buffer.bind_to_storage_buffer(GridBuffer.BIND_CHANNEL)


class VertexArray(object):
    def __init__(self, gl):
        super().__init__()

        self.program = None
        self.vertex_array = None

    def render(self):
        assert self.vertex_array is not None

        self.vertex_array.render()

    def uniform(self, uname, uvalue):
        assert self.program is not None

        if uname not in self.program:
            return

        if isinstance(uvalue, (mat2, mat3, mat4)):
            self.program[uname].write(uvalue)
        elif isinstance(uvalue, (float, int, bool, tuple)):
            self.program[uname] = uvalue
        else:
            print(type(uvalue))


class ParticlesVertexArray(VertexArray):
    def __init__(self, gl, particles_buffer, mvp, width, height):
        super().__init__(gl)
        self.gl = gl

        with open("./gl/particles.vs", "r") as fp:
            particle_vs_source = fp.read()

        with open("./gl/particles.gs", "r") as fp:
            particle_gs_source = fp.read()

        with open("./gl/particles.fs", "r") as fp:
            particle_fs_source = fp.read()

        self.program = gl.program(
            vertex_shader=particle_vs_source,
            geometry_shader=particle_gs_source,
            fragment_shader=particle_fs_source,
        )
        self.vertex_array = gl.vertex_array(
            self.program,
            [(particles_buffer.buffer, "4f 4f 4f", "in_pos", "in_uv", "in_velocity")],
            skip_errors=True,
        )

        self.uniform("u_mvp", mvp)
        self.uniform("u_resolution", (width, height))

        assert self.vertex_array is not None

    def render(self):
        self.vertex_array.render(mode=mg.POINTS)


class PostProcess(VertexArray):
    def __init__(self, gl):
        super().__init__(gl)

        with open("./gl/postprocess.vs") as fp:
            vs_source = fp.read()

        with open("./gl/postprocess.fs") as fp:
            fs_source = fp.read()

        self.program = gl.program(vertex_shader=vs_source, fragment_shader=fs_source)
        self.vertex_array = gl.vertex_array(
            self.program,
            [
                (
                    gl.buffer(
                        np.array(
                            [
                                [-1.0, -1.0, 0.0, 1.0],
                                [-1.0, +1.0, 0.0, 1.0],
                                [+1.0, -1.0, 0.0, 1.0],
                                [+1.0, +1.0, 0.0, 1.0],
                            ],
                            dtype=np.float32,
                        )
                    ),
                    "4f",
                    "in_pos",
                )
            ],
            gl.buffer(np.array((0, 1, 2, 2, 1, 3), dtype=np.int32)),
        )


class Client(object):
    def __init__(self, window):
        super().__init__()

        # create moderngl context
        self.gl = mg.create_context()

        self.window = window

        self.width, self.height = glfw.get_window_size(window)

        imgui.create_context()
        self.imgui = ModernGLGLFWRenderer(
            ctx=self.gl, display_size=(self.width, self.height)
        )
        self.imgui.wire_events(self.gl, window)

        self.perspective = perspectiveFov(
            radians(94.0), self.width, self.height, 0.5, 100.0
        )

        distance = 1.6
        self.prev_time = 0.0
        self.camera_pos = vec3(distance, distance * 0.5, -distance)
        self.lookat = lookAt(self.camera_pos, vec3(0.0, -0.5, 0.0), vec3(0.0, 1.0, 0.0))
        self.mvp = self.perspective * self.lookat
        self.compile_shaders()

        def on_modified(e):
            self.need_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_modified
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

        self.wire_events(window)

    def wire_events(self, window):
        is_drag = False
        prev_pos = ivec2(0, 0)

        def on_resize(window, width, height):
            pass

        def on_cursor_pos(window, x, y):
            nonlocal is_drag
            nonlocal prev_pos

            pos = ivec2(x, y)
            dragged = vec2(pos - prev_pos)
            prev_pos = pos

            if is_drag:
                rotation_speed = 0.05
                c, s = cos(dragged.x * rotation_speed), sin(dragged.x * rotation_speed)
                self.camera_pos.xz = mat2(c, s, -s, c) * self.camera_pos.xz
                self.lookat = lookAt(self.camera_pos, vec3(0.0, -0.5, 0.0), vec3(0.0, 1.0, 0.0))
                self.mvp = self.perspective * self.lookat
                self.particles_vertex_array.uniform("u_mvp", self.mvp)

        def on_mouse_button(window, button, action, mods):
            nonlocal is_drag
            nonlocal prev_pos
            x, y = glfw.get_cursor_pos(window)

            if button == glfw.MOUSE_BUTTON_LEFT:
                if action == glfw.PRESS and mods == glfw.MOD_ALT:
                    is_drag = True
                elif action == glfw.RELEASE:
                    is_drag = False

                prev_pos = ivec2(x, y)

        def on_scroll(window, scroll_x, scroll_y):
            pass

        self.imgui.on_resize = on_resize
        self.imgui.on_cursor_pos = on_cursor_pos
        self.imgui.on_mouse_button = on_mouse_button
        self.imgui.on_scroll = on_scroll

    def compile_shaders(self):
        self.need_compile = False

        try:
            # read and compile compute shaders
            self.simulations = [
                AdvectStage(self.gl),
                PressureStage(self.gl),
                VorticityStage(self.gl),
                EvolveStage(self.gl),
            ]

            # vec4 force, float density, float pressure
            self.particles = ParticlesBuffer(self.gl)
            self.grid = GridBuffer(self.gl)

            self.color = self.gl.texture((self.width, self.height), 4)
            self.gbuffer = self.gl.framebuffer([self.color])
            self.particles_vertex_array = ParticlesVertexArray(
                self.gl, self.particles, self.mvp, self.width, self.height
            )
            self.postprocess = PostProcess(self.gl)

            InjectStage(self.gl).run()

            print("compiled")

        except Exception as e:
            print(e)

    def update(self):
        if self.need_compile:
            self.compile_shaders()
            return

        t = glfw.get_time()
        dt = t - self.prev_time

        self.simulation_step(t, dt)
        self.render()
        self.render_ui(t, dt)

        self.prev_time = t

    def simulation_step(self, t, dt):
        for simulation in self.simulations:
            simulation.uniform("u_time", t)
            simulation.uniform("u_deltatime", dt)
            simulation.run()

    def render(self):
        self.gbuffer.use()
        self.gl.enable_only(mg.CULL_FACE | mg.BLEND)
        self.gl.clear(0.0, 0.0, 0.0)
        self.particles_vertex_array.render()

        self.gl.screen.use()
        self.gl.disable(mg.CULL_FACE)
        self.gl.clear(0.0, 0.0, 0.0)
        self.color.use(0)
        self.postprocess.uniform("gb_color", 0)
        self.postprocess.render()

    def render_ui(self, t, dt):
        imgui.new_frame()

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("Test Menu"):
                imgui.end_menu()

            imgui.end_main_menu_bar()

        imgui.begin("Control")
        imgui.text(f"FPS {1.0 / (dt):.2f}")
        imgui.end()
        imgui.render()

        self.imgui.render(imgui.get_draw_data())


if __name__ == "__main__":
    from main import main

    main()
