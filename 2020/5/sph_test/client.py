import math
from functools import partial

import glfw
import imgui
import moderngl as mg
from glm import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from integrations.imgui import ModernGLGLFWRenderer


NUM_PARTICLES = 5000
NUM_THREADS_PER_GROUP = 128
PATICLE_CS_GROUP_SIZE_X = math.ceil(NUM_PARTICLES / NUM_THREADS_PER_GROUP)

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
        self.process.run(gx, gy, gz)


class StorageBuffer(object):
    def __init__(self, gl):
        super().__init__()
        self.gl = gl


class InjectStage(SimulateStage):
    def __init__(self, gl):
        super().__init__(gl, "./gl/cs_0_inject.glsl")

        self.uniform("u_emitter_position", vec3(0.0, 5.0, 0.0))


class AdvectStage(SimulateStage):
    def __init__(self, gl):
        super().__init__(gl, "./gl/cs_1_advect.glsl")


class PressureStage(SimulateStage):
    def __init__(self, gl):
        super().__init__(gl, "./gl/cs_2_pressure.glsl")


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

        buffer_size = (4 + 2) * NUM_PARTICLES
        self.buffer = self.gl.buffer(reserve=buffer_size)
        self.buffer.bind_to_storage_buffer(ParticlesBuffer.BIND_CHANNEL)


class GridBuffer(StorageBuffer):
    BIND_CHANNEL = 1

    def __init__(self, gl):
        super().__init__(gl)

        buffer_size = (4 + 1 + 1) * NUM_GRID
        self.buffer = self.gl.buffer(reserve=buffer_size)
        self.buffer.bind_to_storage_buffer(GridBuffer.BIND_CHANNEL)


class ParticlesVertexArray(object):
    def __init__(self, gl, particles_buffer):
        super().__init__()
        self.gl = gl

        with open("./gl/particles.vs", "r") as fp:
            particle_vs_source = fp.read()

        with open("./gl/particles.gs", "r") as fp:
            particle_gs_source = fp.read()

        with open("./gl/particles.fs", "r") as fp:
            particle_fs_source = fp.read()

        self.vertex_array = gl.vertex_array(
            gl.program(
                vertex_shader=particle_vs_source,
                geometry_shader=particle_gs_source,
                fragment_shader=particle_fs_source,
            ),
            [(particles_buffer.buffer, "4f 2f", "in_pos", "in_uv")],
        )
        assert self.vertex_array is not None

    def render(self):
        self.vertex_array.render(mode=mg.POINTS)


class Client(object):
    def __init__(self, window):
        super().__init__()

        self.gl = mg.create_context()
        self.window = window

        imgui.create_context()
        self.imgui = ModernGLGLFWRenderer(
            ctx=self.gl, display_size=glfw.get_window_size(window)
        )
        self.imgui.wire_events(self.gl, window)

        self.compile_shaders()

        def on_modified(e):
            self.need_compile = True

        handler = FileSystemEventHandler()
        handler.on_modified = on_modified
        observer = Observer()
        observer.schedule(handler, "./gl", True)
        observer.start()

        self.prev_time = 0.0

    def compile_shaders(self):
        self.need_compile = False

        try:
            # read and compile compute shaders
            self.simulations = [
                InjectStage(self.gl),
                AdvectStage(self.gl),
                PressureStage(self.gl),
                VorticityStage(self.gl),
                EvolveStage(self.gl),
            ]

            # vec4 force, float density, float pressure
            self.particles = ParticlesBuffer(self.gl)
            self.grid = GridBuffer(self.gl)
            self.particles_vertex_array = ParticlesVertexArray(self.gl, self.particles)

            print("compiled")

        except Exception as e:
            print(e)

    def update(self):
        if self.need_compile:
            self.compile_shaders()
            return

        # self.simulation_step()
        self.render()
        self.render_ui()

    def simulation_step(self):
        for simulation in self.simulations:
            simulation.run(1, 1, 1)

    def render(self):
        self.gl.enable_only(mg.CULL_FACE | mg.DEPTH_TEST)
        self.gl.clear(0.0, 0.2, 0.2)
        self.particles_vertex_array.render()

    def render_ui(self):
        imgui.new_frame()

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("A"):
                imgui.end_menu()

            imgui.end_main_menu_bar()

        if True:
            imgui.begin("Control")
            t = glfw.get_time()
            imgui.text(f"FPS {1.0 / (t - self.prev_time):.2f}")
            self.prev_time = t
            imgui.end()

        imgui.render()
        self.imgui.render(imgui.get_draw_data())


if __name__ == "__main__":
    from main import main

    main()
