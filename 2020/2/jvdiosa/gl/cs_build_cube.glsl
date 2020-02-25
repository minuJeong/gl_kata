#version 460

layout(local_size_x=8) in;

struct Vertex
{
    vec4 position;
    vec4 texcoord0;
    vec4 normal;
};

struct Cube
{
    Vertex vertices[6];
};

layout(binding=0) buffer cubes_buffer
{
    Cube cubes[];
};

void main()
{
    uint cube_id = gl_LocalInvocationID.x + gl_WorkGroupID.x * gl_WorkGroupSize.x;

    Cube cube;
    for (uint vtx_id = 0; vtx_id < 6; vtx_id++)
    {
        Vertex vertex;
        cube.vertices[vtx_id] = vertex;
    }
    cubes[cube_id] = cube;
}
