#version 460

in vec4 in_pos;
out vec4 vs_pos;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_perspective;
uniform float u_aspect = 1.0;

void main()
{
    vec4 pos = in_pos;
    vs_pos = pos;
    gl_Position = u_perspective * u_view * u_model * pos;
    gl_Position.x /= u_aspect;
}
