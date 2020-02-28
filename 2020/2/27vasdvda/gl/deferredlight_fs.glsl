#version 460

in vec4 vs_pos;
out vec4 fs_colour;

void main()
{
    vec3 rgb;
    rgb.x = 0.0;
    fs_colour = vec4(rgb, 1.0);
}
