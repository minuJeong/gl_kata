import os

import imageio as ii


path = r"C:\Users\minuh\Desktop"
mov = ii.get_writer("./mov.mp4")

for file in os.listdir(path):
    if not file.endswith(".jpg"):
        continue

    img = ii.imread(f"{path}/{file}")
    mov.append_data(img)

mov.close()
