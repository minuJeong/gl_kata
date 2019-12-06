#version 460
layout(local_size_x=8, local_size_y=8, local_size_z=8) in;

struct Particle
{
    vec4 position;
    vec4 velocity;
    vec4 color;
};

layout(binding=0) buffer vbo
{
    Particle particles[];
};

uniform ivec3 u_particles_dimension;
uniform float u_time; 

void main()
{
    uvec3 xyz = gl_LocalInvocationID.xyz + gl_WorkGroupID.xyz * gl_WorkGroupSize.xyz;
    uint particle_id =
        xyz.x +
        xyz.y * u_particles_dimension.x +
        xyz.z * u_particles_dimension.x * u_particles_dimension.y;

    Particle particle = particles[particle_id];
    // particle.position.xyz += particle.velocity.xyz;

    // particle.position.x = particle.position.x < -1.0 ? +1.0 : particle.position.x;
    // particle.position.x = particle.position.x > +1.0 ? -1.0 : particle.position.x;

    // particle.position.y = particle.position.x < -1.0 ? +1.0 : particle.position.y;
    // particle.position.y = particle.position.x > +1.0 ? -1.0 : particle.position.y;

    // particle.position.z = particle.position.x < -1.0 ? +1.0 : particle.position.z;
    // particle.position.z = particle.position.x > +1.0 ? -1.0 : particle.position.z;

    particles[particle_id] = particle;
}
