#version 460

layout(local_size_x=64) in;

struct Particle
{
    vec4 pos;
    vec4 velocity;
    float scale;
    float rotation;
    uint id;
};

struct Vertex
{
    vec4 pos;
    vec2 uv;
    uint id;
};

layout(std430, binding=0) buffer buffer_vertices
{
    Vertex vertices[];
};

layout(std430, binding=1) buffer buffer_indices
{
    int indices[];
};

layout(std430, binding=2) buffer buffer_particles
{
    Particle particles[];
};

void populate_vertices(Particle particle)
{
    Vertex vertex;
    vertex.id = particle.id;

    vertex.pos = vec4(-1.0, -1.0, 0.0, 1.0);
    vertex.uv = vec2(0.0, 0.0);
    vertices[particle.id * 4 + 0] = vertex;

    vertex.pos = vec4(+1.0, -1.0, 0.0, 1.0);
    vertex.uv = vec2(1.0, 0.0);
    vertices[particle.id * 4 + 1] = vertex;

    vertex.pos = vec4(-1.0, +1.0, 0.0, 1.0);
    vertex.uv = vec2(0.0, 1.0);
    vertices[particle.id * 4 + 2] = vertex;

    vertex.pos = vec4(+1.0, +1.0, 0.0, 1.0);
    vertex.uv = vec2(1.0, 1.0);
    vertices[particle.id * 4 + 3] = vertex;
}

void populate_indices(Particle particle)
{
    indices[particle.id * 6 + 0] = int(particle.id * 6 + 0);
    indices[particle.id * 6 + 1] = int(particle.id * 6 + 2);
    indices[particle.id * 6 + 2] = int(particle.id * 6 + 1);
    indices[particle.id * 6 + 3] = int(particle.id * 6 + 2);
    indices[particle.id * 6 + 4] = int(particle.id * 6 + 1);
    indices[particle.id * 6 + 5] = int(particle.id * 6 + 3);
}

void main()
{
    uint id = uint(gl_LocalInvocationID.x + gl_WorkGroupID.x * gl_WorkGroupSize.x);

    Particle particle = particles[id];
    populate_vertices(particle);
    populate_indices(particle);
}
