import struct

from PySide2 import QtWidgets
import moderngl as mg


VS = """
#version 410
in vec4 in_pos;
out vec4 vs_pos;
void main()
{
    vs_pos = in_pos;
    gl_Position = vs_pos;
}
"""

FS = """
#version 410
in vec4 vs_pos;
out vec4 fs_color;
void main()
{
    fs_color = vec4(1.0, 0.0, 0.0, 1.0);
}
"""


class Client(QtWidgets.QOpenGLWidget):
    def initializeGL(self):
        self.context = mg.create_context()

        program = self.context.program(vertex_shader=VS, fragment_shader=FS)
        vb = self.context.buffer(
            struct.pack(
                "16f",
                *(-1.0, -1.0, 0.0, 1.0),
                * (+1.0, -1.0, 0.0, 1.0),
                * (-1.0, +1.0, 0.0, 1.0),
                * (+1.0, +1.0, 0.0, 1.0)
            )
        )
        ib = self.context.buffer(struct.pack("6i", 0, 1, 2, 2, 1, 3))
        self.vertex_array = self.context.vertex_array(
            program, [(vb, "4f", "in_pos")], ib
        )

    def paintGL(self):
        self.vertex_array.render()


def main():
    app = QtWidgets.QApplication([])
    client = Client()
    client.show()
    app.exec_()


if __name__ == "__main__":
    main()
