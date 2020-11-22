import os
import imageio as ii


writer = ii.get_writer("./movie.mp4")

for filename in os.listdir("/"):
    if not filename.endswith("jpg"):
        continue
    writer.append_data(ii.imread(f"./{filename}"))
writer.close()
