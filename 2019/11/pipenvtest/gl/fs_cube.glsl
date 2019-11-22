#version 460

in vec4 vs_position;
in vec4 vs_normal;
in vec2 vs_texcoord0;

out vec4 fs_color;

void main()
{
    vec3 RGB = abs(vs_position.xyz) * 0.75;
    RGB = max(RGB, 0.2);
    fs_color = vec4(RGB, 1.0);
}
