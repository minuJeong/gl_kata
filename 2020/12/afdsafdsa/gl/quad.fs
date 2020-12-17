#version 460

in vec4 vs_pos;
out vec4 fs_color;

struct Cell
{
    vec4 is_alive;
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

void main()
{
    vec2 uv = vs_pos.xy;
    uv = uv * 0.5 + 0.5;
    uvec2 xy = uvec2(uv * u_resolution.xy);
    uint i = xy.x + xy.y * u_resolution.x;

    vec4 buffer_value = cell_to[i].is_alive.x > 0.5 ? vec4(0.7, 0.7, 0.7, 1.0) : vec4(0.12, 0.12, 0.12, 1.0);

    fs_color = buffer_value;
}
