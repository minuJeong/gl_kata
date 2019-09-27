import math

import numpy as np
import moderngl as mg
import imageio as ii


def shader(path, **kargs):
    with open(path, "r") as fp:
        content = fp.read()

    for k, v in kargs:
        content = content.replace(k, v)

    lines = []
    for line in content.splitlines():
        if line.startswith("#include"):
            line = shader(line.split(" ")[1])
        lines.append(line)

    return "\n".join(lines)


class Renderer(object):
    def __init__(self, W=32, H=32, D=25, Z_HOR=5, Z_VER=5):
        assert D == Z_HOR * Z_VER, "Z_HOR X Z_VER should be equal to D"
        self.W, self.H, self.D = W, H, D
        self.Z_HOR, self.Z_VER = Z_HOR, Z_VER
        self.channels = 4
        self.bytes_per_channel = 4

    def reserve_size(self):
        return self.W * self.H * self.D * self.channels * self.bytes_per_channel

    def compute_group_size(self):
        gx, gy, gz = float(self.W) / 8, float(self.H) / 8, float(self.D) / 8
        gx, gy, gz = math.ceil(gx), math.ceil(gy), math.ceil(gz)
        gx, gy, gz = int(gx), int(gy), int(gz)
        return gx, gy, gz

    def render_volue_tex(self):
        gl = mg.create_standalone_context()
        cs = gl.compute_shader(shader("./gl/compute.glsl"))

        if "u_width" in cs:
            cs["u_width"].value = self.W

        if "u_height" in cs:
            cs["u_height"].value = self.H

        if "u_depth" in cs:
            cs["u_depth"].value = self.D

        if "u_z_hor" in cs:
            cs["u_z_hor"].value = self.Z_HOR

        if "u_z_ver" in cs:
            cs["u_z_ver"].value = self.Z_VER

        self.buffer_0 = gl.buffer(reserve=self.reserve_size())
        self.buffer_0.bind_to_storage_buffer(0)

        cs.run(*self.compute_group_size())

        return self

    def save(self, path):
        pixels = (self.H * self.Z_VER, self.W * self.Z_HOR, self.channels)
        data = self.buffer_0.read()
        data = np.frombuffer(data, dtype="f4")
        data = data.reshape(pixels)
        data = data[::-1]
        data = np.multiply(data, 255.0)
        data = data.astype(np.uint8)
        ii.imwrite(path, data)
        return self


def main():
    W, H, D = 256, 256, 256
    HOR, VER = 16, 16

    print("started")
    renderer = Renderer(W, H, D, HOR, VER)
    print("renderer initialized")

    renderer.render_volue_tex()
    print("rendering finished")

    renderer.save("output_0.png")
    print("saved")

    renderer.save("output_1.png")
    print("saved")

    renderer.save("output_2.png")
    print("saved")

    renderer.save("output_3.png")
    print("saved")

    renderer.save("output_4.png")
    print("saved")


if __name__ == "__main__":
    main()
