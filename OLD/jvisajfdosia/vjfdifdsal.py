
from psd_tools import PSDImage
from psd_tools.api.layers import TypeLayer


path = "./fdsafds.psd"
psd_img = PSDImage.open(path)

for layer in psd_img:
    if not layer.has_pixels():
        continue

    if type(layer) is not TypeLayer:
        continue

    layer.top = 8
    layer.left = 8

psd_img

output_path = "./generated_psd.psd"
psd_img.save(output_path)
