#version 460

layout(local_size_x=4, local_size_y=4, local_size_z=4) in;

layout(binding=0) buffer v0
{
    float density[];
};

uniform uvec3 u_vsize;
uniform ivec2 u_res;

uint xyz_to_i(uvec3 xyz)
{
    return xyz.x + xyz.y * u_vsize.x + xyz.z * u_vsize.x * u_vsize.y;
}

void main()
{
    uvec3 xyz = gl_LocalInvocationID.xyz + gl_WorkGroupID.xyz * gl_WorkGroupSize.xyz;
    uint i = xyz_to_i(xyz);

    density[i] = 1.0;
}
