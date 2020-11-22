import os

import numpy as np
import imageio as ii


prev_mov_reader = ii.get_reader("./mov.mp4")
prev_mov_data = np.array([f for f in prev_mov_reader])

path = r"C:\Users\minuh\Desktop"
mov = ii.get_writer("./mov_test.mp4")
for f in prev_mov_data:
    mov.append_data(f)

# for file in os.listdir(path):
#     if not file.endswith(".jpg"):
#         continue

#     img = ii.imread(f"{path}/{file}")
#     mov.append_data(img)

mov.close()
