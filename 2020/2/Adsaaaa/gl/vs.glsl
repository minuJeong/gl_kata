#version 460

in vec4 in_pos;
out VS_OUT
{
    vec4 vs_pos;
} vs_out;

uniform float u_screen_aspect = 1.0;

void main()
{
    vs_out.vs_pos = in_pos;
    gl_Position = vs_out.vs_pos;
    gl_Position.x /= u_screen_aspect;
}
