_any = any

from glm import *


class Util(object):
    binary_types = [vec2, vec3, vec4, mat2, mat3, mat4]

    def __init__(self):
        raise Exception("static class!")

    @staticmethod
    def load_shader(path):
        with open(path, "r") as fp:
            return fp.read()

    @staticmethod
    def uniform(programs, data):
        for p in programs:
            for n, v in data.items():
                if n not in p:
                    continue

                if _any(filter(lambda t: isinstance(v, t), Util.binary_types)):
                    p[n].write(v)
                else:
                    p[n].value = v
