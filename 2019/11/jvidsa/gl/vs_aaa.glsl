#version 460

in vec2 in_pos;
out vec2 vs_pos;

void main()
{
    vs_pos = in_pos;

    gl_Position = vec4(vs_pos, 0.0, 1.0);
}
