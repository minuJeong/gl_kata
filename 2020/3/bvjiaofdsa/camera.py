from glm import *

from transform import Transform
from const import UP


class Camera(object):

    transform = None
    fov = radians(74.0)
    near = 0.01
    far = 1000.0
    width, height = 1, 1

    def __init__(self):
        super(Camera, self).__init__()
        self.transform = Transform()
        self.transform.pos = vec3(-2.0, 3.0, -7.0)
        self.transform.rot = quat_cast(lookAt(self.transform.pos, vec3(0.0), UP))

    def get_mat(self):
        v = self.transform.get_mat()
        p = perspective(self.fov, self.width / self.height, self.near, self.far)
        return p * v


if __name__ == "__main__":
    from main import main

    main()
