import csv

import numpy as np


class Loader(object):
    def __init__(self):
        raise Exception("static class!")

    @staticmethod
    def load_vbo(path):
        with open(path, "r") as fp:
            reader = csv.reader(fp)
            data = np.array([row for row in reader])

            position0 = data[1:, 1:4]
            position1 = data[1:, 4:8]
            position2 = data[1:, 8:12]
            position3 = data[1:, 12:16]
            position4 = data[1:, 16:18]
            position5 = data[1:, 18:22]
            position6 = data[1:, 22:26]
            texcoord0 = data[1:, 26:30]
            texcoord1 = data[1:, 30:34]
            texcoord2 = data[1:, 34:38]
            texcoord3 = data[1:, 38:42]
            texcoord4 = data[1:, 42:46]
            texcoord5 = data[1:, 46:50]
            texcoord6 = data[1:, 50:54]
            texcoord7 = data[1:, 54:58]

        return np.hstack(
            (
                position0,
                position1,
                position2,
                position3,
                position4,
                position5,
                position6,
                texcoord0,
                texcoord1,
                texcoord2,
                texcoord3,
                texcoord4,
                texcoord5,
                texcoord6,
                texcoord7,
            )
        ).astype(np.float32)

    @staticmethod
    def load_ibo(path):
        with open(path, "r") as fp:
            content = fp.read()

        indices = []
        for line in content.splitlines():
            try:
                indices.append(int(line))

            except ValueError:
                continue

        return np.array(indices).astype(np.int32)

    @staticmethod
    def load_shader(path):
        with open(path, "r") as fp:
            content = fp.read()

        lines = []
        inc = "#include "
        for line in content.splitlines():
            if not line.startswith(inc):
                lines.append(line)
            else:
                inc_path = line.split(inc)[1]
                lines.append(Loader.load_shader(inc_path))
        return "\n".join(lines)
