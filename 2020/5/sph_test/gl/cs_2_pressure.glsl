#version 460

#define GRID_RES 12

layout(local_size_x=4, local_size_y=4, local_size_z=4) in;

struct Particle
{
    vec4 position;
    vec4 velocity;
    vec4 texcoord0;
};

layout(binding=0) buffer particles_buffer
{
    Particle particles[];
};

struct Grid
{
    vec4 velocity;
    float density;
};

layout(binding=1) buffer grid_buffer
{
    Grid grids[];
};

void main()
{
    uint i = gl_GlobalInvocationID.x + gl_GlobalInvocationID.y * 64 + gl_GlobalInvocationID.z * 256;
    Particle particle = particles[i];

    vec3 grid_xyz = floor(particle.position.xyz * GRID_RES);
    uint g = uint(grid_xyz.x + grid_xyz.y * GRID_RES + grid_xyz.z * GRID_RES * GRID_RES);
    Grid grid = grids[g];

    particles[i] = particle;
    grids[g] = grid;
}
