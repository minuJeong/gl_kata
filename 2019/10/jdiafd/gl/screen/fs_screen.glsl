#version 460

in vec2 vs_pos;
in vec2 vs_uv;

out vec4 fs_color;

void main()
{
    fs_color = vec4(vs_uv, 0.0, 1.0);
}
