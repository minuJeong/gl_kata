from glm import *


class Transform(object):
    def __init__(self, pos=None, rot=None, scale=None):
        super(Transform, self).__init__()
        self.pos = pos or vec3(0.0)
        self.rot = rot or quat_cast(mat4(1.0))
        self.scale = scale or vec3(1.0)

    def get_mat(self):
        return translate(mat4(1.0), self.pos)

        return (
            mat4_cast(self.rot) if not isinstance(self.rot, mat4) else self.rot
        ) * translate(mat4(1.0), self.pos)

        return scale(
            (mat4_cast(self.rot) if not isinstance(self.rot, mat4) else self.rot)
            * translate(mat4(1.0), self.pos),
            self.scale,
        )


if __name__ == "__main__":
    from main import main

    main()
