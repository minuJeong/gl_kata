import moderngl as mg
from PyQt5 import QtWidgets
from PyQt5.Qt import Qt


class Render(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(Render, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def initializeGL(self):
        self.gl = mg.create_context()


def main():
    app = QtWidgets.QApplication([])
    render = Render()
    render.show()
    app.exec()


if __name__ == "__main__":
    main()
