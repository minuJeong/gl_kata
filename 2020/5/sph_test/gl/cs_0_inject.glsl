#version 460

#define NUM_PARTICLES 20000

layout(local_size_x=4, local_size_y=4, local_size_z=4) in;

struct Particle
{
    vec4 position;
};

layout(binding=0) buffer particles
{
    Particle particle_position[];
};

struct Cell
{
    vec4 velocity;
};

layout(binding=1) buffer grid
{
    Cell cell[];
};

uniform vec3 u_emitter_position;

void main()
{
    uvec3 uvw = gl_LocalInvocationID.xyz + gl_WorkGroupID.xyz * gl_WorkGroupSize.xyz;

    vec3 pos = u_emitter_position + vec3(-0.5, -1.0, 0.0);

    Particle particle;

    for (int i = 0; i < 10; i++)
    {
        particle.position = vec4(-1.0 + 0.01 * i, -1.0, 0.0, 1.0);
        particle_position[i] = particle;
    }
}
