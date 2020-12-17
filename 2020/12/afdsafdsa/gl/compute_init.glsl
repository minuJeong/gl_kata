#version 460

layout(local_size_x=8, local_size_y=8) in;

struct Cell
{
    vec4 is_alive;
    vec4 color;
};

layout(binding=0) buffer buffer_0
{
    Cell cell_from[];
};

layout(binding=1) buffer buffer_1
{
    Cell cell_to[];
};

uniform uvec2 u_resolution;

highp float hash(vec2 uv)
{
    highp float x = dot(uv, vec2(12.4321, 45.4231));
    return fract(cos(x) * 43125.4321);
}

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;
    uint i = xy.x + xy.y * u_resolution.x;

    vec2 uv = vec2(xy) / vec2(u_resolution.xy);

    Cell cell;
    cell.is_alive = vec4(hash(uv) < 0.1 ? 1 : 0, 0, 0, 1);
    cell_from[i] = cell;
}
