#version 460
#include ./gl/common.glsl

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer vertex_buffer
{
    Vertex vertices[];
};

layout(binding=1) buffer index_buffer
{
    Face faces[];
};

uniform uint u_width;
uniform uint u_height;

void main()
{
    uint vertex_index = gl_LocalInvocationID.x + gl_WorkGroupID.x * gl_WorkGroupSize.x;
    vertices[vertex_index].pos = vec3(1.0, 1.0, 0.0);
}
