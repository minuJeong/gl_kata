#version 460

in vec3 in_pos;
in vec3 in_normal;

out vec3 vs_pos;
out vec3 vs_normal;

uniform mat4 u_MVP;

void main()
{
    vs_pos = in_pos;
    vs_normal = in_normal;
    gl_Position = u_MVP * vec4(vs_pos, 1.0);
}
