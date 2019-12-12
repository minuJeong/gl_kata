#version 460

in vec4 in_pos;
out vec4 vs_pos;

uniform float u_aspect = 1.0;

void main()
{
    vs_pos = in_pos;
    gl_Position = vs_pos;
    gl_Position.x /= u_aspect;
}
