#version 460

in vec2 vs_pos;
out vec4 fs_color;

void main()
{
    fs_color = vec4(vs_pos * 0.5 + 0.5, 0.0, 1.0);
}
