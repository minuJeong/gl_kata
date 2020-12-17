import numpy as np
import moderngl as mg
import imageio as ii


def read_render_buffer(render_buffer, shape):
    return np.multiply(np.frombuffer(render_buffer.read(), dtype=np.float32).reshape(shape), 255.0).astype(np.uint8)


def main():
    W, H = 128, 128
    RW, RH = 512, 512

    gl = mg.create_standalone_context(require=460)

    init = gl.compute_shader(open("./init.glsl").read())
    update = gl.compute_shader(open("./update.glsl").read())
    render = gl.compute_shader(open("./render.glsl").read())

    b0 = gl.buffer(reserve=W * H * 4)
    b1 = gl.buffer(reserve=W * H * 4)
    render_buffer = gl.buffer(reserve=RW * RH * 4 * 4)

    render_buffer.bind_to_storage_buffer(2)

    b0.bind_to_storage_buffer(0)

    gx, gy = W // 8, H // 8
    rgx, rgy = RW // 8, RH // 8
    init.run(gx, gy)

    record = ii.get_writer("./render.mp4")

    for i in range(60):
        b0.bind_to_storage_buffer(i % 2)
        b1.bind_to_storage_buffer((i + 1) % 2)
        update.run(gx, gy)

        render.run(rgx, rgy)

        record.append_data(read_render_buffer(render_buffer, (RH, RW, 4)))

    record.close()


if __name__ == '__main__':
    main()
