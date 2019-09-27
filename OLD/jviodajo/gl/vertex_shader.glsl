#version 460

in vec4 in_pos;
out vec4 vs_pos;
out vec2 vs_uv0;

uniform vec2 u_resolution;

void main()
{
    vs_pos = in_pos;
    vs_uv0 = vs_pos.zw;
    gl_Position = vec4(vs_pos.xy, 0.0, 1.0);
}
