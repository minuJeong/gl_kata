#version 460

in vec4 in_pos;
out vec2 vs_uv;
out vec2 vs_pos;

void main()
{
    vs_pos = in_pos.xy;
    vs_uv = in_pos.zw;

    gl_Position = vec4(vs_pos, 0.0, 1.0);
}
