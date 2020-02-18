#version 460

struct Particle
{
    vec4 pos;
    vec4 velocity;
    float scale;
    float rotation;
    uint id;
};

layout(std430, binding=2) buffer buffer_particles
{
    Particle particles[];
};

mat4 transform_from_particle(Particle particle)
{
    return mat4(
        particle.scale, 0.0,            0.0,            0.0,
        0.0,            particle.scale, 0.0,            0.0,
        0.0,            0.0,            particle.scale, 0.0,
        particle.pos.x, particle.pos.y, particle.pos.z, 1.0
    );
}

in vec4 in_pos;
in vec2 in_uv;
in uint in_id;

out vec4 vs_pos;
out vec2 vs_uv;
out uint vs_id;

void main()
{
    vs_pos = in_pos;
    vs_uv = in_uv;
    vs_id = in_id;

    Particle particle = particles[vs_id];
    mat4 mvp = transform_from_particle(particle);

    gl_Position = mvp * vs_pos;
}
