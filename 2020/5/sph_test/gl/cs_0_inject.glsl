#version 460

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
    uint i = gl_GlobalInvocationID.x + gl_GlobalInvocationID.y * 64 + gl_GlobalInvocationID.z * 256;

    vec3 xyz = vec3(gl_GlobalInvocationID.xyz);
    float x = xyz.x, y = xyz.y, z = xyz.z;

    vec3 velocity = vec3(0.0);
    velocity.x = cos(float(i) * 0.001);
    velocity.y = -0.1;
    velocity.z = sin(float(i) * 0.001);
    velocity = normalize(velocity) * 0.05;

    vec3 position = vec3(0.0);

    Particle particle;
    particle.position = vec4(position, 1.0);
    particle.velocity = vec4(velocity, 0.0);
    particle.texcoord0 = vec4(x, y, z, 1.0);    
    particles[i] = particle;
}
