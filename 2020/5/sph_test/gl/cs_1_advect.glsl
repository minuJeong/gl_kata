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

uniform float u_time = 0.0;
uniform float u_deltatime = 0.1;


float sdf_box(vec3 pos, vec3 box)
{
    vec3 b = abs(pos) - box;
    return length(max(b, 0.0)) + min(max(b.x, max(b.y, b.z)), 0.0);
}

float hash12(vec2 uv)
{
    return fract(cos(dot(uv, vec2(12.43215, 45.43215))) * 43215.43215);
}

void cage(inout vec3 pos, inout vec3 vel)
{
    const float SIZE = 1.0;
    const float BOUNCE = 0.34;
    const float INERTIA = 0.94;

    vec3 bbox_min = vec3(-SIZE, -SIZE, -SIZE);
    vec3 bbox_max = vec3(+SIZE, +SIZE, +SIZE);

    if (pos.x < bbox_min.x || pos.x > bbox_max.x)
    {
        vel.x *= -BOUNCE;
    }

    if (pos.y < bbox_min.y || pos.y > bbox_max.y)
    {
        vel.y *= -BOUNCE;
    }

    if (pos.z < bbox_min.z || pos.z > bbox_max.z)
    {
        vel.z *= -BOUNCE;
    }
    pos = min(max(pos, bbox_min), bbox_max);
}

Grid get_grid(vec3 pos, inout uint g)
{
    vec3 grid_xyz = floor(pos * GRID_RES);
    g = uint(grid_xyz.x + grid_xyz.y * GRID_RES + grid_xyz.z * GRID_RES * GRID_RES);
    Grid grid = grids[g];
    return grid;
}

void main()
{
    uint i = gl_GlobalInvocationID.x + gl_GlobalInvocationID.y * 64 + gl_GlobalInvocationID.z * 256;
    Particle particle = particles[i];

    uint g = 0;
    Grid grid = get_grid(particle.position.xyz, g);

    particle.position += particle.velocity * u_deltatime;
    vec3 pos = particle.position.xyz;
    vec3 vel = particle.velocity.xyz;

    cage(pos, vel);
    vel.y -= 0.02;

    particle.position.xyz = pos.xyz;
    particle.velocity.xyz = vel.xyz;
    particles[i] = particle;

    grid.velocity = vec4(0.0);
    grid.density = 0.0;
    grids[g] = grid;
}
