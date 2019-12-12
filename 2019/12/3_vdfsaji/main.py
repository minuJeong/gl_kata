import struct
import random
from itertools import chain

from glm import *
import moderngl as mg
import numpy as np
import imageio as ii
import glfw
import pybullet as pb

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


ZERO = vec3(0.0)
LEFT = vec3(-1.0, 0.0, 0.0)
RIGHT = vec3(1.0, 0.0, 0.0)
UP = vec3(0.0, 1.0, 0.0)
DOWN = vec3(0.0, -1.0, 0.0)
FORWARD = vec3(0.0, 0.0, 1.0)
BACK = vec3(0.0, 0.0, -1.0)

WIDTH, HEIGHT = 1024, 1024

bin_types = tuple(
    chain(
        (vec2, vec3, vec4,),
        (mat2, mat3, mat4,),
        (ivec2, ivec3, ivec4,),
        (uvec2, uvec3, uvec4,),
    )
)


def read_shader(path):
    with open(path, "r") as fp:
        return fp.read()


def read_mesh(path):
    with open(path, "rb") as fp:
        return fp.read()


def uniform(p, n, v):
    def apply(__p):
        if isinstance(v, bin_types):
            __p[n].write(bytes(v))
        else:
            __p[n].value = v

    if not isinstance(p, list):
        p = [p]

    for _p in p:
        if n in _p:
            apply(_p)


class Materials(object):
    _programs = {}

    @staticmethod
    def recompile(gl):
        Materials._programs = {}

    @staticmethod
    def program(gl, key):
        if key not in Materials._programs:
            Materials._programs[key] = gl.program(
                vertex_shader=read_shader(f"./gl/vs_{key}.glsl"),
                fragment_shader=read_shader(f"./gl/fs_{key}.glsl"),
            )
        return Materials._programs[key]

    @staticmethod
    def allprograms():
        return list(Materials._programs.values())


class RenderObject(object):
    """ Abstract class for renderable objects """

    @property
    def model(self):
        T = translate(mat4(1.0), vec3(self.pos.x, self.pos.y, 0.0))
        R = mat4_cast(self.rotation)
        S = mat4(self.scale)
        return S * R * T

    def __init__(self, gl, pos, rotation=None, scale=None):
        super(RenderObject, self).__init__()
        assert isinstance(scale, (type(None), float))

        self.gl = gl
        self.pos = pos
        self.rotation = rotation or quat(1.0, 0.0, 0.0, 0.0)
        self.scale = scale or 1.0
        self.vao = None

    def render(self):
        if self.vao:
            self.vao.render()


class Quad(RenderObject):
    VB, IB = read_mesh("./mesh/quad.vb"), read_mesh("./mesh/quad.ib")

    @staticmethod
    def recompile():
        Quad.VB, Quad.IB = read_mesh("./mesh/quad.vb"), read_mesh("./mesh/quad.ib")

    def __init__(self, gl, pos):
        super(Quad, self).__init__(gl, pos)

        vbo = gl.buffer(Quad.VB)
        vbo_content = [(vbo, "4f", "in_pos")]
        ibo = gl.buffer(Quad.IB)
        self.program = Materials.program(gl, "node")
        self.vao = gl.vertex_array(self.program, vbo_content, ibo)

        self.col_id = pb.createCollisionShape(pb.GEOM_BOX, halfExtents=[1.0, 1.0, 1.0])
        self.col_debug_id = pb.createVisualShape(pb.GEOM_BOX, halfExtents=[1.0, 1.0, 1.0])
        pb.createMultiBody(0.0, self.col_id, self.col_debug_id, [*pos], [*self.rotation])


class Ray(RenderObject):
    def __init__(self, gl, pos, tar, **kargs):
        super(Ray, self).__init__(gl, pos)

        ray_width = kargs["width"] if "width" in kargs else 0.2

        vertices = list(
            chain(
                [pos.x, pos.y + ray_width, pos.z, 1.0],
                [pos.x, pos.y - ray_width, pos.z, 1.0],
                [tar.x, tar.y + ray_width, tar.z, 1.0],
                [tar.x, tar.y - ray_width, tar.z, 1.0],
                [pos.x + ray_width, pos.y, pos.z, 1.0],
                [pos.x - ray_width, pos.y, pos.z, 1.0],
                [tar.x + ray_width, tar.y, tar.z, 1.0],
                [tar.x - ray_width, tar.y, tar.z, 1.0],
            )
        )
        self.VB = struct.pack(f"{len(vertices)}f", *vertices)
        self.IB = struct.pack("6i", 0, 1, 2, 2, 1, 3)

        vbo = gl.buffer(self.VB)
        vbo_content = [(vbo, "4f", "in_pos")]
        ibo = gl.buffer(self.IB)
        self.program = Materials.program(gl, "ray")
        self.vao = gl.vertex_array(self.program, vbo_content, ibo)

        self.color = vec3(1.0, 1.0, 0.0)

    def set_color(self, color):
        self.color = color

    def render(self):
        uniform(self.program, "u_color", self.color)
        super(Ray, self).render()


class Node(Quad):
    def __init__(self, gl, x, y, pos):
        super(Node, self).__init__(gl, pos)
        self.x, self.y = x, y
        self.color = ZERO if random.random() < 0.5 else vec3(1.0)

    def set_id(self, idx):
        self.idx = idx

    def set_color(self, color):
        self.color = color

    def render(self):
        uniform(self.program, "u_model", self.model)
        uniform(self.program, "u_idx", self.idx)
        uniform(self.program, "u_color", self.color)
        super(Node, self).render()


class PostProcess(RenderObject):
    def __init__(self, gl):
        super(PostProcess, self).__init__(gl, vec3(0.0))

        vbo = gl.buffer(Quad.VB)
        vbo_content = [(vbo, "4f", "in_pos")]
        ibo = gl.buffer(Quad.IB)
        self.program = Materials.program(gl, "postprocess")
        self.vao = gl.vertex_array(self.program, vbo_content, ibo)

    def render(self):
        uniform(self.program, "u_gb_color", 0)
        super(PostProcess, self).render()


class Client(object):
    def __init__(self, window, width, height):
        super(Client, self).__init__()
        self.window = window
        self.width, self.height = width, height

        self.gl = mg.create_context()

        MSAA = 2
        self.gb_color = self.gl.texture((width * MSAA, height * MSAA), 4)
        self.gbuffer = self.gl.framebuffer([self.gb_color])

        self.init_input()
        self.compile_scene()

        h = FileSystemEventHandler()
        h.on_modified = self.on_modified
        o = Observer()
        o.schedule(h, "./gl/", True)
        o.start()

    def init_input(self):
        self.is_drag = False
        self.drag_prepos = vec2(0.0, 0.0)
        self.camera_pos = vec3(0.0, 0.0, -120.0)
        view = lookAt(self.camera_pos, ZERO, UP) * vec4(0.0, 0.0, 1.0, 1.0)
        print(view)
        self.camera_rot = quat(1.0, 0.0, 0.0, 0.0)
        help(quat)

        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(self.window, self.on_mouse_pos)
        glfw.set_window_size_callback(self.window, self.on_window_size)
        glfw.set_scroll_callback(self.window, self.on_scroll)

    def compile_scene(self):
        self.should_compile = False

        if hasattr(self, "scene"):
            for (x, y), node in self.scene.items():
                del node

            Materials.recompile(self.gl)
            Quad.recompile()

        self.scene = {}
        self.debug_scene = []
        self.MAXX, self.MAXY = -1, -1

        ix = 0
        for x in np.arange(-20.0, 20.0, 2.2):
            iy = 0
            for y in np.arange(-20.0, 20.0, 2.2):
                self.scene[ix, iy] = Node(self.gl, ix, iy, vec3(x, y, 0.0))
                iy += 1
            ix += 1

        self.MAXX = ix
        self.MAXY = iy

        for (x, y), node in self.scene.items():
            node.set_id(x + y * ix)

        idx_start = (random.randrange(self.MAXX - 2), random.randrange(self.MAXY - 2))
        idx_target = (
            random.randrange(idx_start[0], self.MAXX - 1),
            random.randrange(idx_start[1], self.MAXY - 1),
        )

        startnode, targetnode = self.scene[idx_start], self.scene[idx_target]
        startnode.set_color(vec3(1.0, 0.0, 0.0))
        targetnode.set_color(vec3(0.0, 0.0, 1.0))
        uniform(
            Materials.program(self.gl, "node"), "u_aspect", self.width / self.height
        )

        self.post_process = PostProcess(self.gl)

    def apply_camera(self):
        self.view = mat4_cast(self.camera_rot)
        uniform(Materials.allprograms(), "u_view", self.view)

        self.perspective = perspective(radians(74.0), WIDTH / HEIGHT, 0.01, 1000.0)
        uniform(Materials.allprograms(), "u_perspective", self.perspective)

    # NOT USED
    def render_to_texture(self):
        render_tex_color = gl.texture((WIDTH, HEIGHT), 4)
        fbo = gl.framebuffer([render_tex_color])
        fbo.use()

        self.render()

        img = (
            np.frombuffer(render_tex_color.read(), dtype=np.ubyte)
            .reshape((HEIGHT, WIDTH, 4))
            .astype(np.uint8)
        )
        img = img[::-1]
        ii.imwrite("render_output.png", img)

    def render(self):
        if self.should_compile:
            self.compile_scene()

        self.apply_camera()
        self.gbuffer.clear(depth=1.0)
        self.gbuffer.use()

        for (x, y), node in self.scene.items():
            node.render()

        for debug_entity in self.debug_scene:
            debug_entity.render()

        self.gl.screen.use()
        self.gb_color.use(0)
        self.post_process.render()

    def on_modified(self, e):
        self.should_compile = True

    def on_mouse_button(self, window, button, action, mods):
        if mods == 0:
            x, y = glfw.get_cursor_pos(window)
            x, y = x / WIDTH, y / HEIGHT
            if action == glfw.PRESS:

                if button == glfw.MOUSE_BUTTON_LEFT:
                    self.is_drag = True
                    self.drag_prepos = vec2(x, y)

                elif button == glfw.MOUSE_BUTTON_RIGHT:
                    pass

            elif action == glfw.RELEASE:
                if button == glfw.MOUSE_BUTTON_LEFT:
                    self.is_drag = False
                    self.drag_prepos = vec2(x, y)

                elif button == glfw.MOUSE_BUTTON_RIGHT:
                    ray_from = self.camera_pos
                    camdir = (self.perspective * self.view * vec4(ray_from, 1.0)).xyz
                    ray_to = self.camera_pos + camdir * 1000.0

                    ray = Ray(self.gl, ray_from, ray_to)
                    self.debug_scene.append(ray)

                    rayquery = pb.rayTest([*self.camera_pos], [*ray_to])[0]
                    objid, linkid, fract, pos, norm = rayquery
                    if objid > 0:
                        print("OBJID FOUND", objid, linkid, fract, pos, norm)

    def on_window_size(self, window, width, height):
        self.gl.viewport = (0, 0, width, height)
        aspect = width / int(max(height, 1))
        uniform(Materials.program(self.gl, "node"), "u_aspect", aspect)

    def on_mouse_pos(self, window, x, y):
        x, y = x / WIDTH, y / HEIGHT
        px, py = self.drag_prepos
        dx, dy = x - px, y - py

        if self.is_drag:
            c, s = cos(-dx), sin(-dx)
            xz = mat2(c, -s, s, c) * self.camera_pos.xz
            self.camera_pos = vec3(xz.x, self.camera_pos.y, xz.y)
            self.camera_pos = (
                rotate(mat4(1.0), -dy, LEFT) * vec4(self.camera_pos, 1.0)
            ).xyz

        self.drag_prepos = vec2(x, y)

    def on_scroll(self, window, x, y):
        camdir = (lookAt(self.camera_pos, ZERO, UP) * vec4(FORWARD, 1.0)).xyz
        self.camera_pos += camdir * y * 0.1


def init():
    pb.connect(pb.DIRECT)

    glfw.init()
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    window = glfw.create_window(WIDTH, HEIGHT, "ASTAR", None, None)
    glfw.make_context_current(window)

    client = Client(window, WIDTH, HEIGHT)

    pb.setGravity(0.0, 0.0, 0.0)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        pb.stepSimulation()
        client.render()
        glfw.swap_buffers(window)

    pb.disconnect()
    print("window closed")


def main():
    init()


if __name__ == "__main__":
    main()
