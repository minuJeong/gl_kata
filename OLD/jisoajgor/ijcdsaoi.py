
import moderngl as mg
import numpy as np


def read(path):
    with open(path, 'r') as fp:
        return fp.read()


class GPUService(object):

    def __init__(self):
        super(GPUService, self).__init__()

        self.w, self.h = 512, 512

    def generate_image(self):
        """
        """

        gl = mg.create_standalone_context()

        buf0 = gl.buffer(reserve=self.w * self.h * 4 * 4)
        buf0.bind_to_storage_buffer(0)

        cs = gl.compute_shader(read("./gl/compute.glsl"))
        cs.run()

        img = np.frombuffer(buf0.read(), dtype=np.float32)
        img = np.multiply(img, 255.0)
        img = img.reshape((self.h, self.w, 4))
        img = img.astype(np.uint8)


service = GPUService()
service.generate_image()
