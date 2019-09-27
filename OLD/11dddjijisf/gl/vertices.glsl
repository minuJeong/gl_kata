#version 460

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform mat4 u_MVP;

in vec3 in_pos;
in vec3 in_normal;

out vec3 vs_pos;
out vec2 vs_uv;
out vec3 vs_normal;

void main()
{
    vs_pos = in_pos;
    vs_uv = in_pos.xy * 0.5 + 0.5;
    vs_normal = in_normal;

    gl_Position = u_MVP * vec4(in_pos, 1.0);
}
