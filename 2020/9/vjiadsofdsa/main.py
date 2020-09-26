import moderngl as mg
import numpy as np
import imageio as ii


SIZE = 512


def main():
    gl = mg.create_context(standalone=True, require=460)

    cs = gl.compute_shader(
        source="""
#version 460
layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer b_0
{
    vec4 x[];
};

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;

    vec2 uv = vec2(xy) / 512.0;

    uint index = xy.x * 512 + xy.y;
    x[index] = vec4(uv.xy, 0.0, 1.0);
}
"""
    )

    gl_buffer = gl.buffer(reserve=SIZE * SIZE * 4 * 4)
    gl_buffer.bind_to_storage_buffer(0)

    cs.run(SIZE // 8, SIZE // 8)

    data = np.multiply(np.frombuffer(gl_buffer.read(), dtype=np.float32), 255.0)
    data = data.reshape(SIZE, SIZE, 4).astype(np.uint8)

    ii.imwrite("output.png", data)


if __name__ == "__main__":
    main()
