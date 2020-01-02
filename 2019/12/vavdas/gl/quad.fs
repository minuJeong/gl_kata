#version 460

in vec2 vs_pos;
out vec4 fs_color;

uniform float u_time;

void main()
{
    fs_color = vec4(1.0, 0.0, 0.0, 1.0);
}
