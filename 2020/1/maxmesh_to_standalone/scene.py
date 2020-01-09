from glm import *

from mesh import NSightMesh


class _SceneMesh(object):
    def __init__(self, gl):
        super(_SceneMesh, self).__init__()
        self.gl = gl
        self.transform = mat4(1.0)
        self.init()

    def init(self):
        """ override to perform initialization """
        pass


class Pegasus(_SceneMesh):
    def init(self):
        vs, fs = "./gl/nsight_default.vs", "./gl/nsight_default.fs"

        self.transform = translate(mat4(1.0), vec3(2.0, 0.0, 0.0))

        print("reading pegasus wings..")
        vbo, ibo = "./mesh/pegasus_wings.vbo", "./mesh/pegasus_wings.ibo"
        self.pegasus_wings = NSightMesh(vbo, ibo, vs, fs)
        self.pegasus_wings.build_vao(self.gl)

        print("reading pegasus head..")
        vbo, ibo = "./mesh/pegasus_head.vbo", "./mesh/pegasus_head.ibo"
        self.pegasus_head = NSightMesh(vbo, ibo, vs, fs)
        self.pegasus_head.build_vao(self.gl)

        print("reading pegasus body..")
        vbo, ibo = "./mesh/pegasus_body.vbo", "./mesh/pegasus_body.ibo"
        self.pegasus_body = NSightMesh(vbo, ibo, vs, fs)
        self.pegasus_body.build_vao(self.gl)

        print("reading pegasus decal..")
        vbo, ibo = "./mesh/pegasus_decal.vbo", "./mesh/pegasus_decal.ibo"
        self.pegasus_decal = NSightMesh(vbo, ibo, vs, fs)
        self.pegasus_decal.build_vao(self.gl)

        self.compile()

    def compile(self):
        print("compiling material..")
        self.pegasus_wings.build_material(self.gl)
        self.pegasus_head.build_material(self.gl)
        self.pegasus_body.build_material(self.gl)
        self.pegasus_decal.build_material(self.gl)

    def render(self, MVP=None, VP=None):
        if MVP is None:
            VP = VP or mat4(1.0)
            MVP = VP * self.transform

        self.pegasus_wings.render(self.gl, MVP=MVP)
        self.pegasus_head.render(self.gl, MVP=MVP)
        self.pegasus_body.render(self.gl, MVP=MVP)
        self.pegasus_decal.render(self.gl, MVP=MVP)


class Minotaur(_SceneMesh):
    def init(self):
        vs, fs = "./gl/nsight_default.vs", "./gl/nsight_default.fs"

        self.transform = translate(mat4(1.0), vec3(-2.0, 0.0, 0.0))

        print("reading minotaur body..")
        vbo, ibo = "./mesh/minotaur_body.vbo", "./mesh/minotaur_body.ibo"
        self.minotaur_body = NSightMesh(vbo, ibo, vs, fs)
        self.minotaur_body.build_vao(self.gl)

        print("reading minotaur head..")
        vbo, ibo = "./mesh/minotaur_head.vbo", "./mesh/minotaur_head.ibo"
        self.minotaur_head = NSightMesh(vbo, ibo, vs, fs)
        self.minotaur_head.build_vao(self.gl)

        print("reading minotaur leg..")
        vbo, ibo = "./mesh/minotaur_leg.vbo", "./mesh/minotaur_leg.ibo"
        self.minotaur_leg = NSightMesh(vbo, ibo, vs, fs)
        self.minotaur_leg.build_vao(self.gl)

        print("reading minotaur deco..")
        vbo, ibo = "./mesh/minotaur_body_deco.vbo", "./mesh/minotaur_body_deco.ibo"
        self.minotaur_deco = NSightMesh(vbo, ibo, vs, fs)
        self.minotaur_deco.build_vao(self.gl)

        print("reading minotaur deco2..")
        vbo, ibo = "./mesh/minotaur_body_deco_2.vbo", "./mesh/minotaur_body_deco_2.ibo"
        self.minotaur_deco2 = NSightMesh(vbo, ibo, vs, fs)
        self.minotaur_deco2.build_vao(self.gl)

        self.compile()

    def compile(self):
        self.minotaur_body.build_material(self.gl)
        self.minotaur_head.build_material(self.gl)
        self.minotaur_leg.build_material(self.gl)
        self.minotaur_deco.build_material(self.gl)
        self.minotaur_deco2.build_material(self.gl)

    def render(self, MVP=None, VP=None):
        if MVP is None:
            VP = VP or mat4(1.0)
            MVP = VP * self.transform

        self.minotaur_body.render(self.gl, MVP=MVP)
        self.minotaur_head.render(self.gl, MVP=MVP)
        self.minotaur_leg.render(self.gl, MVP=MVP)
        self.minotaur_deco.render(self.gl, MVP=MVP)
        self.minotaur_deco2.render(self.gl, MVP=MVP)
