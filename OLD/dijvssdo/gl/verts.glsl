#version 460

in vec2 in_pos;

out vec2 vs_uv;
out vec2 vs_pos;

void main()
{
    vs_pos = in_pos;
    vs_uv = in_pos * 0.5 + 0.5;
    gl_Position = vec4(vs_pos, 0.0, 1.0);
}
