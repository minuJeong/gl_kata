#version 460

in vec4 in_pos;
out vec4 vs_pos;

void main()
{
    vs_pos = in_pos;
    gl_Position = vs_pos;
}
