#version 460

in vec3 in_pos;

out vec3 vs_pos;
out vec2 vs_uv;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform mat4 u_MVP;

void main()
{
    vs_pos = in_pos;
    gl_Position = u_MVP * vec4(in_pos, 1.0);
}
