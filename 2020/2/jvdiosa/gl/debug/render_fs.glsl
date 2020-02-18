#version 460

in vec4 vs_pos;
out vec4 fs_colour;

void main()
{
    fs_colour = vs_pos;
    fs_colour.w = 1.0;
}
