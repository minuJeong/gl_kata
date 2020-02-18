import numpy as np


vertices = None
with open("./mesh/Box001.vbo", "rb") as fp:
    vertices = fp.read()

vertices_array = np.frombuffer(vertices, dtype=np.float32)
vertices_array = vertices_array.reshape((-1, 4))
print(vertices_array.astype(np.float32))
