#version 460

in vec4 in_pos;
in vec4 in_texcoord;
in vec4 in_normal;

out vec4 vs_pos;

uniform mat4 u_MVP = mat4(1.0);

void main()
{
    vs_pos = in_pos;
    gl_Position = u_MVP * in_pos;
}
