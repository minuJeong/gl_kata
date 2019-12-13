#version 460

in vec4 vs_pos;
out vec4 fs_color;

struct Const
{
    float u_aspect;
    float u_time;
};

layout(binding=14) buffer constbuffer
{
    Const b_const;
};

void main()
{
    fs_color = vs_pos;
}
