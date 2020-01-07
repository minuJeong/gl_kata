from glm import *

from mesh import NSightMesh


class Pegasus(object):
    def __init__(self, gl):
        super(Pegasus, self).__init__()
        self.init(gl)

    def init(self, gl):
        vs, fs = "./gl/nsight_default.vs", "./gl/nsight_default.fs"

        pegasus_transform = translate(mat4(1.0), vec3(2.0, 0.0, 0.0))

        print("reading pegasus wings..")
        vbo, ibo = "./mesh/pegasus_wings.vbo", "./mesh/pegasus_wings.ibo"
        self.pegasus_wings = NSightMesh(vbo, ibo, vs, fs)
        self.pegasus_wings.build_vao(gl)
        self.pegasus_wings.set_transform(pegasus_transform)

        print("reading pegasus head..")
        vbo, ibo = "./mesh/pegasus_head.vbo", "./mesh/pegasus_head.ibo"
        self.pegasus_head = NSightMesh(vbo, ibo, vs, fs)
        self.pegasus_head.build_vao(gl)
        self.pegasus_head.set_transform(pegasus_transform)

        print("reading pegasus body..")
        vbo, ibo = "./mesh/pegasus_body.vbo", "./mesh/pegasus_body.ibo"
        self.pegasus_body = NSightMesh(vbo, ibo, vs, fs)
        self.pegasus_body.build_vao(gl)
        self.pegasus_body.set_transform(pegasus_transform)

        print("reading pegasus decal..")
        vbo, ibo = "./mesh/pegasus_decal.vbo", "./mesh/pegasus_decal.ibo"
        self.pegasus_decal = NSightMesh(vbo, ibo, vs, fs)
        self.pegasus_decal.build_vao(gl)
        self.pegasus_decal.set_transform(pegasus_transform)

        self.compile(gl)

    def compile(self, gl):
        self.pegasus_wings.build_material(gl)
        self.pegasus_head.build_material(gl)
        self.pegasus_body.build_material(gl)
        self.pegasus_decal.build_material(gl)

    def render(self, gl, VP):
        self.pegasus_wings.render(gl, VP)
        self.pegasus_head.render(gl, VP)
        self.pegasus_body.render(gl, VP)
        self.pegasus_decal.render(gl, VP)


class Minotaur(object):
    def __init__(self, gl):
        super(Minotaur, self).__init__()
        self.init(gl)

    def init(self, gl):
        vs, fs = "./gl/nsight_default.vs", "./gl/nsight_default.fs"

        minotaur_transform = translate(mat4(1.0), vec3(-2.0, 0.0, 0.0))

        print("reading minotaur body..")
        vbo, ibo = "./mesh/minotaur_body.vbo", "./mesh/minotaur_body.ibo"
        self.minotaur_body = NSightMesh(vbo, ibo, vs, fs)
        self.minotaur_body.build_vao(gl)
        self.minotaur_body.set_transform(minotaur_transform)

        print("reading minotaur head..")
        vbo, ibo = "./mesh/minotaur_head.vbo", "./mesh/minotaur_head.ibo"
        self.minotaur_head = NSightMesh(vbo, ibo, vs, fs)
        self.minotaur_head.build_vao(gl)
        self.minotaur_head.set_transform(minotaur_transform)

        print("reading minotaur leg..")
        vbo, ibo = "./mesh/minotaur_leg.vbo", "./mesh/minotaur_leg.ibo"
        self.minotaur_leg = NSightMesh(vbo, ibo, vs, fs)
        self.minotaur_leg.build_vao(gl)
        self.minotaur_leg.set_transform(minotaur_transform)

        print("reading minotaur deco..")
        vbo, ibo = "./mesh/minotaur_body_deco.vbo", "./mesh/minotaur_body_deco.ibo"
        self.minotaur_deco = NSightMesh(vbo, ibo, vs, fs)
        self.minotaur_deco.build_vao(gl)
        self.minotaur_deco.set_transform(minotaur_transform)

        print("reading minotaur deco2..")
        vbo, ibo = "./mesh/minotaur_body_deco_2.vbo", "./mesh/minotaur_body_deco_2.ibo"
        self.minotaur_deco2 = NSightMesh(vbo, ibo, vs, fs)
        self.minotaur_deco2.build_vao(gl)
        self.minotaur_deco2.set_transform(minotaur_transform)

        self.compile(gl)

    def compile(self, gl):
        self.minotaur_body.build_material(gl)
        self.minotaur_head.build_material(gl)
        self.minotaur_leg.build_material(gl)
        self.minotaur_deco.build_material(gl)
        self.minotaur_deco2.build_material(gl)

    def render(self, gl, VP):
        self.minotaur_body.render(gl, VP)
        self.minotaur_head.render(gl, VP)
        self.minotaur_leg.render(gl, VP)
        self.minotaur_deco.render(gl, VP)
        self.minotaur_deco2.render(gl, VP)
