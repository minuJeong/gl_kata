#version 460

in vec4 in_pos;
in vec4 in_vel;

out vec4 vs_pos;
out vec4 vs_vel;

uniform float u_aspect = 1.0;

void main()
{
    vs_pos = in_pos;
    vs_pos.x /= u_aspect;
    gl_Position = vec4(vs_pos);
}
