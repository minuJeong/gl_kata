#version 460

struct CONST
{
    vec4 u_campos;
};

layout(binding=0) buffer constbuffer
{
    CONST constants;
};

layout(location=0) in vec3 in_pos_0;
layout(location=1) in vec4 in_pos_1;

out vec3 vs_pos;

void main()
{
    vs_pos = in_pos_0.xyz;

    gl_Position = vec4(vs_pos, 1.0);
}
