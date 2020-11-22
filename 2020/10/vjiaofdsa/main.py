import os

import imageio as ii
import numpy as np
import moderngl as mg


gl = mg.create_standalone_context(require=460)
cs = gl.compute_shader(open("./gl/process.comp").read())

TARGET_DIR = "C:/STORE/IMG/GREENSHOTS/"
image_files = []
for filepath in os.listdir(TARGET_DIR):
    if not filepath.endswith(".png"):
        continue

    image_files.append(f"{TARGET_DIR}/{filepath}")

for img_0_path in image_files:
    for img_1_path in image_files:
        if img_0_path == img_1_path:
            continue

        print("", img_0_path, "\n", img_1_path)

        img_0 = ii.imread(img_0_path)
        img_1 = ii.imread(img_1_path)

        height, width = img_0.shape[0], img_0.shape[1]

        if img_0.shape[2] != 4:
            img_0_canvas = np.zeros(shape=(height, width, 4), dtype=np.uint8)
            img_0_canvas[:height, :width, :img_0.shape[2]] = img_0[:]
            img_0 = img_0_canvas

        if "u_resolution" in cs:
            cs["u_resolution"] = (width, height)

        img_0_buffer = gl.buffer(img_0)
        img_0_buffer.bind_to_storage_buffer(0)

        img_1_buffer = gl.buffer(img_1)
        img_1_buffer.bind_to_storage_buffer(1)

        output_buffer = gl.buffer(reserve=width * height * 4)
        output_buffer.bind_to_storage_buffer(2)

        gx, gy = width // 8, height // 8
        cs.run(gx, gy)

        output_img_buffer = output_buffer.read()
        output_img = np.frombuffer(output_img_buffer, dtype=np.uint8)
        output_img = output_img.reshape(img_0.shape)
        ii.imwrite("output_0.png", output_img)

        break
    break
