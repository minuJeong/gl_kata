#version 460

in vec4 in_pos;
out vec4 fs_color;

uniform vec3 u_color;

void main()
{
    fs_color = vec4(u_color, 1.0);
}
