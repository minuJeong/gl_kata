#version 460

in vec2 vs_pos;
out vec4 fs_color;

const vec3 UP = vec3(0.0, 1.0, 0.0);

void main()
{
    vec2 uv = vs_pos;
    vec3 RGB;
    RGB = 0.1 - uv.yyy * 0.08;
    fs_color = vec4(RGB, 1.0);
}
