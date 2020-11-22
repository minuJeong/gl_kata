#version 460

in vec4 in_pos;
out vec4 vs_pos;

uniform mat4 u_mvp;

void main()
{
    vs_pos = in_pos;
    gl_Position = u_mvp * vs_pos;
}
