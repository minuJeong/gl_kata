#version 460

in vec4 in_pos;
out vec4 vs_pos;

uniform mat4 u_model = mat4(1.0);
uniform mat4 u_mvp = mat4(1.0);

void main()
{
    vs_pos = in_pos;
    gl_Position = u_mvp * vs_pos;
}
