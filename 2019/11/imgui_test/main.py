import bimpy as b
from PIL import Image


c = b.Context()
c.init(1200, 1200, "bimpy test")

img = Image.new("RGBA", (512, 512), )
px = img.load()
for x in range(512):
    for y in range(512):
        r = int(255.0 * float(x) / 512.0)
        g = int(255.0 * float(y) / 512.0)
        px[x, y] = (r, g, max(255 - r - g, 0), 255)

b_img = b.Image(img)

b_f1 = b.Float()
b_f2 = b.Float()
b_f3 = b.Float()

while not c.should_close():
    with c:
        b.text("hi")
        if b.button("cat"):
            print("mew")

        b.input_float("float1", b_f1, 0.0, 1.0)
        b.image(b_img)
        b.slider_float3("float", b_f1, b_f2, b_f3, 0.0, 1.0)
