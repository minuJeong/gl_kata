import time

import moderngl as mg
import numpy as np
import imageio as ii
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


width, height = 1024, 1024
gx, gy = width // 8, height // 8


def fileread(path):
    content = None
    with open(path, "r") as fp:
        content = fp.read()
    return content


def uniform(p, n, v):
    if n in p:
        p[n] = v


class Watch(object):
    _isdirty = False

    def __init__(self):
        super(Watch, self).__init__()

        self.gl = mg.create_standalone_context(require=460)
        self.out_buffer = self.gl.buffer(reserve=width * height * 4 * 4)
        self.out_buffer.bind_to_storage_buffer(0)

    def serialize_img(self):
        img = np.frombuffer(self.out_buffer.read(), dtype=np.float32)
        img = img.reshape((height, width, 4))
        img = np.multiply(img, 255.0).astype(np.uint8)
        return img

    def set_dirty(self):
        self._isdirty = True

    def execute(self):
        self._isdirty = False

        try:
            cs_source = fileread("./gl/cs_adavd.glsl")

            if cs_source.startswith("--"):
                return True

            print("compiling shader..")
            cs = self.gl.compute_shader(cs_source)

            print("recording shader..")
            uniform(cs, "u_res", (width, height))

            # preview image
            cs.run(gx, gy)
            ii.imwrite("output.png", self.serialize_img())

            if "# ++" not in cs_source:
                writer = ii.get_writer("./output.mp4", fps=30)
                for i in range(120):
                    uniform(cs, "u_frame", i)
                    cs.run(gx, gy)

                    img = self.serialize_img()
                    writer.append_data(img)

                    if i % 30 == 0:
                        print(f"\t recording at {(i // 30) + 1} sec..")

                writer.close()

            print("executed")

        except Exception as e:
            print(e)

        return False

    def watch(self):
        handler = FileSystemEventHandler()
        handler.on_modified = lambda e: self.set_dirty()
        observer = Observer()
        observer.schedule(handler, "./gl")
        observer.start()

        self.execute()

        while True:
            if not self._isdirty:
                time.sleep(0.01)
                continue

            if self.execute():
                break

        print("exit")


def main():
    Watch().watch()


if __name__ == "__main__":
    main()
