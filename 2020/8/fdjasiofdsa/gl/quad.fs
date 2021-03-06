#version 460

in vec4 vs_pos;
out vec4 fs_color;

void main()
{
    vec2 uv = vs_pos.xy * 0.5 + 0.5;
    fs_color = vec4(uv, 0.0, 1.0);
}
