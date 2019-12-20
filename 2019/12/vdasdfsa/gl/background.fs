#version 460

in vec2 vs_pos;
layout(location=0) out vec4 fs_color;

void main()
{
    vec3 RGB = vec3(0.04);
    fs_color = vec4(RGB, 1.0);
}
