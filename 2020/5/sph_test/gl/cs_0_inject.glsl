#version 460

layout(local_size_x=8, local_size_x=8) in;

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

struct Cell
{
    vec4 velocity;
};

layout(binding=1) buffer grid
{
    Cell cell[];
};

uniform vec3 u_emitter_position;

float hash12(vec2 uv)
{
    return fract(cos(dot(uv, vec2(12.43215, 45.43215))) * 43215.43215);
}

float hash13(vec3 uvw)
{
    return fract(cos(dot(uvw, vec3(12.43215, 45.43215, 767.43215))) * 43215.43215);
}

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;
    vec3 xyz = vec3(xy.x, 0.0, xy.y);
    vec3 uvw = xyz / vec3(8 * 64);

    float x = xyz.x, y = xyz.y, z = xyz.z;

    vec3 velocity = vec3(uvw);
    velocity.x += hash12(velocity.yz);
    velocity.y += hash12(velocity.xz);
    velocity.z += hash12(velocity.xy);
    velocity = normalize(velocity) * 0.02;

    Particle particle;
    particle.position = vec4(uvw, 1.0);
    particle.velocity = vec4(velocity, 0.0);
    particle.texcoord0 = vec4(x, y, z, 1.0);

    int i = int(xyz.x * 4 * 4 + xyz.y * 4 + xyz.z);
    particles[i] = particle;
}
