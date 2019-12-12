#version 460

in vec4 in_pos;
out vec4 vs_pos;

uniform mat4 u_view;
uniform mat4 u_perspective;

void main()
{
    vs_pos = in_pos;
    gl_Position = u_perspective * u_view * vs_pos;
}
