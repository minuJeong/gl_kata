from glm import *


def _uniform(p, n, v):
    if n in p:
        p[n] = v


def mat_to_16f(m):
    vs = []
    for row in m:
        for v in row:
            vs.append(v)
    return tuple(vs)


WIDTH, HEIGHT = 1920, 1080
TITLE = "hello kata"

UP = vec3(0.0, 1.0, 0.0)
