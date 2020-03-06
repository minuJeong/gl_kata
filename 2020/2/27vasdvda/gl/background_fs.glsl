#version 460

in vec4 vs_pos;
out vec4 fs_colour;

void main()
{
    fs_colour = vec4(1.0, 0.3, 1.0, 1.0) * ((vs_pos.y * 0.5 + 0.5) * 0.1 + 0.1);
}
