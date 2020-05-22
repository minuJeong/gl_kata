#version 460

in vec4 vs_pos;
out vec4 fs_color;

void main()
{
    fs_color = vs_pos;
}
