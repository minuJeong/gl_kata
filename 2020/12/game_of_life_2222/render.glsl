#version 460
#define WIDTH 128
#define RENDERWIDTH 512

layout(local_size_x=8, local_size_y=8) in;

layout(binding=1) buffer b1
{
    bool is_live_to[];
};

layout(binding=2) buffer render_buffer
{
    vec4 colour[];
};

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;
    vec2 uv = vec2(xy) / vec2(RENDERWIDTH, RENDERWIDTH);
    uvec2 bxy = uvec2(floor(uv * WIDTH));

    colour[xy.x + xy.y * RENDERWIDTH] = is_live_to[bxy.x + bxy.y * WIDTH] ? vec4(0.8, 0.4, 0.3, 1.0) : vec4(0.12, 0.3, 0.32, 1.0);
}
