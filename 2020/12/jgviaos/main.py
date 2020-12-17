import numpy as np
import moderngl as mg
import imageio as ii


def main():
    buffer_width, buffer_height = 64, 64
    render_width, render_height = 1024, 1024

    gl = mg.create_standalone_context(require=460)

    cs_game_of_life_init = gl.compute_shader(open("./cs_game_of_life_init.glsl").read())
    cs_game_of_life_update = gl.compute_shader(open("./cs_game_of_life_update.glsl").read())
    cs_render = gl.compute_shader(open("./cs_render.glsl").read())

    b0 = gl.buffer(reserve=buffer_width * buffer_height * 4)
    b1 = gl.buffer(reserve=buffer_width * buffer_height * 4)
    b2 = gl.buffer(reserve=render_width * render_height * 4 * 4)

    b2.bind_to_storage_buffer(2)

    writer = ii.get_writer("./record.mp4", fps=12)

    def read_render(b):
        return np.multiply(np.frombuffer(b.read(), dtype=np.float32).reshape((render_height, render_width, 4)), 255.0).astype(np.uint8)

    gx, gy = buffer_width // 8, buffer_height // 8
    b0.bind_to_storage_buffer(0)
    cs_game_of_life_init.run(gx, gy)
    for i in range(60):
        b0.bind_to_storage_buffer(i % 2)
        b1.bind_to_storage_buffer((i + 1) % 2)

        cs_game_of_life_update.run(gx, gy)
        cs_render.run(render_width // 8, render_height // 8)

        writer.append_data(read_render(b2))

    writer.close()


if __name__ == "__main__":
    main()
