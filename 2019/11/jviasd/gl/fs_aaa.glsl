#version 460

in vec3 vs_pos;
in vec3 vs_normal;

out vec4 fs_color;

void main()
{
    fs_color = vec4(vs_pos, 1.0);
}
