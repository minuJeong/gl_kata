from PySide2 import QtWidgets


class QCustomButton(QtWidgets.QPushButton):
    def __init__(self, title):
        super(QCustomButton, self).__init__()
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        label = QtWidgets.QLabel(title)
        label.setStyleSheet("font-size: 48px")
        layout.addWidget(label)


button = QCustomButton("Hello")
button.show()
