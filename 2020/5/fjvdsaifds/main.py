from psd_tools import PSDImage
import numpy as np
import imageio as ii


psd = PSDImage.open("jfvioadsf.psd")

img_array = None
size = (1, 1)
for layer in psd:
    if layer.name == "Layer 1":
        pixels = layer.composite()
        img_array = np.array(pixels)
        size = pixels.size
        break


assert img_array is not None

images = {}
for y, row in enumerate(img_array):
    for x, pixel in enumerate(row):
        if pixel[0] == 255 and pixel[1] == 255 and pixel[2] == 255 and pixel[3] == 0:
            continue

        xyzw = (pixel[0], pixel[1], pixel[2], pixel[3])
        if xyzw in images:
            images[xyzw][y, x] = pixel

        else:
            images[xyzw] = np.zeros((size[1], size[0], 4))
            images[xyzw][y, x] = pixel

i = 0
for xyzw, img in images.items():
    print(img.shape)
    ii.imwrite(f"output_{i}.png", img)
    i += 1
