#version 460
#define WIDTH 128
#define RENDERWIDTH 512

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer b0
{
    bool is_live_from[];
};

float hash(vec2 uv)
{
    float x = dot(uv, vec2(12.4321, 44.34245));
    return fract(cos(x) * 43215.43);
}

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;

    vec2 uv = vec2(xy) / vec2(WIDTH, WIDTH);
    is_live_from[xy.x + xy.y * WIDTH] = hash(uv) > 0.5;
}
