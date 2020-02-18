import numpy as np
from openpyxl import load_workbook


book = load_workbook("./test.xlsx", read_only=True)
array = np.zeros((1024, 1024))
for row in book.active:
    print("-----", row)
    for cell in row:
        if isinstance(cell.value, (str)):
            print(cell.value.encode("utf8"))

        else:
            print(cell.value)
