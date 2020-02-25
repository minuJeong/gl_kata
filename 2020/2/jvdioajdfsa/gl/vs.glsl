#version 460

layout(binding=2) buffer constants
{
    float u_aspect;
    float u_time;
};

in vec4 in_pos;
out vec4 vs_pos;

void main()
{
    vec4 pos = in_pos;
    gl_Position = pos;
    pos.x *= u_aspect;
    vs_pos = pos;
}
