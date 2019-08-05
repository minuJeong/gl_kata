#version 460

layout(local_size_x=8, local_size_y=8) in;
layout(binding=0) buffer bind_0
{
    vec4 buf0[];
};

uniform uint u_width;
uniform uint u_height;

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;
    uint i = xy.x + xy.y * u_width;

    buf0[i] = vec4(1.0, 0.0, 0.0, 1.0);
}
