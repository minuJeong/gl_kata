#version 460

in vec4 in_pos;
in vec4 in_normal;

out vec4 vs_pos;
out vec4 vs_normal;

uniform mat4 u_MVP;

void main()
{
    vs_pos = in_pos;
    vs_normal = in_normal * 0.5 + 0.5;
    gl_Position = u_MVP * vs_pos;
}
