#version 460
layout(local_size_x=4, local_size_y=4, local_size_z=4) in;

struct Voxel
{
    vec3 velocity;
    float pressure;
};

layout(binding=0) buffer b_0
{
    Voxel voxels[];
};

const uint WIDTH = 128;
const uint HEIGHT = 128;
const uint DEPTH = 128;


uint i(uvec3 xyz) { return xyz.x + xyz.y * HEIGHT + xyz.z * HEIGHT * DEPTH; }

void main()
{
    uvec3 id =  gl_LocalInvocationID.xyz + gl_WorkGroupID.xyz * gl_WorkGroupSize.xyz;
}
