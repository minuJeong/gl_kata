#version 460
#define BUFFER_WIDTH 64
#define RENDER_WIDTH 1024

layout(local_size_x=8, local_size_y=8) in;

layout(binding=1) buffer b1
{
    bool is_alive_to[];
};

layout(binding=2) buffer b2
{
    vec4 colour[];
};

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;
    uint i = xy.x + xy.y * RENDER_WIDTH;

    vec2 uv = vec2(xy) / vec2(RENDER_WIDTH, RENDER_WIDTH);
    uvec2 bxy = uvec2(floor(uv * BUFFER_WIDTH));
    uint bi = bxy.x + bxy.y * BUFFER_WIDTH;

    colour[i] = is_alive_to[bi] ? vec4(0.7, 0.2, 0.1, 1.0) : vec4(0.2, 0.2, 0.2, 1.0);
}
