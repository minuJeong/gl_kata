#version 460

in vec4 in_position;
in vec4 in_normal;
in vec2 in_texcoord0;

out vec4 vs_position;
out vec4 vs_normal;
out vec2 vs_texcoord0;

uniform mat4 u_M;
uniform mat4 u_V;
uniform mat4 u_P;
uniform mat4 u_MVP = mat4(1.0);

void main()
{
    vs_position = in_position;
    vs_normal = in_normal;
    vs_texcoord0 = in_texcoord0;

    gl_Position = u_MVP * in_position;
    gl_PointSize = 400.0;
}
