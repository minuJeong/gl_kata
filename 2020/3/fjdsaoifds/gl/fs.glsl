#version 460

in vec4 vs_pos;
out vec4 fs_colour;

void main()
{
    vec2 uv = vs_pos.xy;
    fs_colour = vec4(uv, 0.0, 1.0);
}
