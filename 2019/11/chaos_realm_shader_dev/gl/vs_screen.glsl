#version 460

in vec4 in_pos;
in vec2 in_texcoord;
out vec4 vs_pos;
out vec2 vs_texcoord;

void main()
{
    vs_pos = in_pos;
    vs_texcoord = in_texcoord;
    gl_Position = vec4(vs_pos);
}
