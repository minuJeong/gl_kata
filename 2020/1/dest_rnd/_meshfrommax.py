import os

import numpy as np
import MaxPlus as mp


dirname = "{}/mesh".format(os.path.dirname(__file__))
if not os.path.isdir(dirname):
    os.makedirs(dirname)

for node in mp.SelectionManager.Nodes:
    node_name = node.GetName()

    mesh_mod = mp.Factory.CreateObjectModifier(mp.ClassIds.Edit_Mesh)
    node.AddModifier(mesh_mod)
    node.Collapse()
    node_object = node.GetObject()
    tri_object = mp.TriObject._CastFrom(node_object)
    mesh = tri_object.GetMesh()
    mesh.CheckNormals(True)

    vertices = []
    num_verts = node.GetVertexCount()
    num_normals = mesh.GetNormalCount()
    mesh.GetNormalsBuilt()
    for i in range(num_verts):
        pos = mesh.GetVertex(i)
        normal = mesh.GetRenderedVertexNormal(i)
        vertices.append([pos.GetX(), pos.GetZ(), pos.GetY(), 1.0])
        vertices.append([normal.GetX(), normal.GetZ(), normal.GetY(), 1.0])
    vertices_array = np.array(vertices, dtype=np.float32)

    indices = []
    num_faces = mesh.GetNumFaces()
    for i in range(num_faces):
        face = mesh.GetFace(i)
        v0 = int(face.GetVert(0))
        v1 = int(face.GetVert(1))
        v2 = int(face.GetVert(2))
        indices.append([v0, v1, v2])
    indices_array = np.array(indices, dtype=np.int32)

    with open("{}/{}.vbo".format(dirname, node_name), "wb") as fp:
        fp.write(vertices_array.tobytes())

    with open("{}/{}.ibo".format(dirname, node_name), "wb") as fp:
        fp.write(indices_array.tobytes())
