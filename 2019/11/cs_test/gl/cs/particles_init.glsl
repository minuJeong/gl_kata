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

float random(vec3 pos)
{
    return fract(sin(dot(pos, vec3(32.123, 12.4321, 667.2431)) * 43214.614321));
}

void main()
{
    uvec3 xyz = gl_LocalInvocationID.xyz + gl_WorkGroupID.xyz * gl_WorkGroupSize.xyz;
    uint particle_id =
        xyz.x +
        xyz.y * u_particles_dimension.x +
        xyz.z * u_particles_dimension.x * u_particles_dimension.y;

    vec3 pos = vec3(
        random(vec3(xyz.xyz)),
        random(vec3(xyz.yxz)),
        random(vec3(xyz.zyx))
    ) * 2.0 - 1.0;

    Particle particle = particles[particle_id];
    particle.position.xyz = vec3(xyz.xyz) / vec3(u_particles_dimension);
    particles[particle_id] = particle;
}
