#version 460

layout(local_size_x=2, local_size_y=2, local_size_z=2) in;

layout(std430, binding=0) buffer vbo
{
    vec4 position[];
};

layout(std430, binding=1) buffer ibo
{
    int index[];
};

void main()
{
    uvec3 xyz = gl_LocalInvocationID.xyz;
    uint i = xyz.x + xyz.y * 2 + xyz.z * 4;

    vec3 pos = xyz * 2.0 - 1.0;
}
