from PySide2 import QtWidgets


def main():
    app = QtWidgets.QApplication([])
    table = QtWidgets.QTableWidget()
    table.setStyleSheet("QTableView::item:selected {background-color: #FF0000;}")
    table.setColumnCount(4)
    table.insertRow(0)
    item = QtWidgets.QTableWidgetItem()
    item.setText("hi")
    table.setItem(0, 0, item)
    table.show()
    app.exec_()


if __name__ == "__main__":
    main()
