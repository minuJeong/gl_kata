#version 460

in vec3 in_pos;
out vec4 vs_pos;

uniform mat4 u_MVP = mat4(1.0);

void main()
{
    vs_pos = vec4(in_pos, 1.0);
    gl_Position = u_MVP * vs_pos;
}
