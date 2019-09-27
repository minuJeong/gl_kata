"""
author: minu jeong
"""

import moderngl as mg
import numpy as np
import imageio as ii


u_width, u_height = 512, 512


def set_uniform(p, n, v):
    if p and n in p:
        p[n].value = v


gl = mg.create_standalone_context()

cs = gl.compute_shader(
    """
#version 460

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer bind_0
{
    vec4 data_0[];
};

uniform uint u_width;

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * 8;
    uint i = xy.x + xy.y * u_width;

    data_0[i] = vec4(1.0, 0.0, 0.0, 1.0);
}

"""
)

set_uniform(cs, "u_width", u_width)

data_0 = gl.buffer(reserve=u_width * u_height * 4 * 4)
data_0.bind_to_storage_buffer(0)

gx, gy = int(u_width / 8), int(u_height / 8)
cs.run(gx, gy)

data = np.frombuffer(data_0.read(), np.float32)
data = np.multiply(data, 255.0)
data = data.reshape((u_height, u_width, 4))
data = data[::-1]
data = data.astype(np.uint8)

ii.imwrite("output.png", data)
