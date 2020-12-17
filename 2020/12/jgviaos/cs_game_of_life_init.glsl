#version 460
#define BUFFER_WIDTH 64
#define RENDER_WIDTH 1024

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer b0
{
    bool is_alive_from[];
};

float hash(vec2 uv)
{
    float x = dot(uv, vec2(12.1423, 43.514));
    return fract(cos(x) * 43215.43);
}

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;
    uint i = xy.x + xy.y * BUFFER_WIDTH;

    vec2 uv = vec2(xy) / vec2(BUFFER_WIDTH, BUFFER_WIDTH);
    float hashed = hash(uv);

    is_alive_from[i] = hashed > 0.5;
}
