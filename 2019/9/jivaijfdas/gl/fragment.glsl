#version 460

in vec2 vs_pos;
in vec2 vs_uv;

out vec4 fs_color;

uniform float u_width;
uniform float u_height;

void main()
{
    vec2 resolution = vec2(u_width, u_height);

    vec3 RGB = vec3(vs_uv, 0.5);
    if (vs_uv.x > 1.0 || vs_uv.x < 0.0)
    {
        RGB = vec3(1.0, 0.0, 0.0);
    }

    fs_color = vec4(RGB, 1.0);
}
