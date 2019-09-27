#version 460

in vec2 in_pos;

out vec2 vs_pos;
out vec2 vs_uv;

void main()
{
    vs_pos = in_pos;
    vs_uv = in_pos * 0.5 + 0.5;
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
