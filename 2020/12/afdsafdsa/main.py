import moderngl as mg
import numpy as np
import imageio as ii


WIDTH, HEIGHT = 512, 512
CHANNELS = 4
SIZE_BYTE = 4


gl = mg.create_standalone_context(require=460)

cs = gl.compute_shader("""
#version 460

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer in_buffer
{
    vec4 colour[];
};

uniform uint u_width;
uniform uint u_height;

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;
    uint i = xy.x + xy.y * u_width;

    vec2 uv = vec2(xy) / vec2(u_width, u_height);

    colour[i] = vec4(uv, 0.0, 1.0);
}
""")

in_buffer = gl.buffer(reserve=WIDTH * HEIGHT * CHANNELS * SIZE_BYTE)
in_buffer.bind_to_storage_buffer(0)

if "u_width" in cs:
    cs["u_width"] = WIDTH

if "u_height" in cs:
    cs["u_height"] = HEIGHT

cs.run(WIDTH // 8, HEIGHT // 8)

output = np.frombuffer(in_buffer.read(), dtype=np.float32).reshape((HEIGHT, WIDTH, CHANNELS))
output = np.multiply(output, 255.0).astype(np.uint8)[::-1]
ii.imwrite("./output.png", output)
