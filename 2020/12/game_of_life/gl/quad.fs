#version 460

in vec4 vs_pos;
out vec4 fs_color;

struct Cell
{
    ivec4 is_alive;
    vec4 color;
};

layout(binding=0) buffer cells_buffer_from
{
    Cell cells_from[];
};

layout(binding=1) buffer cells_buffer_to
{
    Cell cells_to[];
};

uniform int u_map_size = 256;
uniform ivec2 u_pos;
uniform int u_is_drag;

void main()
{
    vec2 uv = vs_pos.xy;
    uv = uv * 0.5 + 0.5;
    vec2 xy = floor(uv * u_map_size);

    int i = int(xy.x + xy.y * u_map_size);
    Cell self = cells_from[i];

    float x = self.is_alive.x == 1 ? 1.0 : self.color.x;
    vec3 rgb = self.color.xyz * x;

    fs_color = vec4(rgb, 1.0);
}
