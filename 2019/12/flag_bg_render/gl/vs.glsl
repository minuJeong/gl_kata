#version 460

layout(std430, binding=5) buffer constbuffer
{
    float u_time;
    float u_aspect;
};

in vec4 in_pos;
out vec4 vs_pos;

void main()
{
    vs_pos = in_pos;
    gl_Position = vs_pos;
}
