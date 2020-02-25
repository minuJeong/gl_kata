#version 460

struct Particle
{
    vec4 pos;
    vec4 velocity;
    float scale;
    float rotation;
    uint id;
};

layout(local_size_x=64) in;

layout(std430, binding=2) buffer buffer_particles
{
    Particle particles[];
};

void advant_particle(uint id)
{
    Particle particle;
    particle.id = id;
    particle.pos = vec4(0.0, 0.0, 0.0, 1.0);
    particle.scale = 0.01;
    particles[id] = particle;
}

void main()
{
    uint id = uint(gl_LocalInvocationID.x + gl_WorkGroupID.x * gl_WorkGroupSize.x);
    
    advant_particle(id);
}
