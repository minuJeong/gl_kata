#version 460

layout(local_size_x=64) in;

struct Particle
{
    vec4 position;
    vec4 velocity;
    float weight;
    float cursor_bound;
    vec2 padding;
};

struct VectorGrid
{
    vec4 velocity;
    float pressure;
};

layout(binding=0) buffer particles
{
    Particle b_particles[];
};

layout(binding=1) buffer vector_field
{
    VectorGrid b_vectors[];
};

uniform uvec3 u_grid_res;
uniform float u_time;
uniform vec2 u_cursor;

float random(float x)
{
    return fract(sin(x * 123.4321) * 341444.43124321);
}

void push_pressure(Particle particle)
{
    vec4 p = particle.position;
    uvec3 xyz = uvec3(p.xyz / u_grid_res);
    uint i = xyz.x + xyz.y * u_grid_res.x + xyz.z * u_grid_res.x * u_grid_res.y;

    VectorGrid vf = b_vectors[i];
    vf.pressure += particle.weight * length(particle.velocity);
    b_vectors[i] = vf;
}

void main()
{
    float local_id = float(gl_LocalInvocationID.x + gl_WorkGroupID.x) * 0.4321;
    uint i = gl_LocalInvocationID.x + gl_WorkGroupID.x * gl_WorkGroupSize.x;

    float speed = random(local_id) * 2.14 + 0.66;

    Particle p = b_particles[i];
    p.position.xyz += p.velocity.xyz;
    if (p.position.x < -1.0)
    {
        p.position.x = +1.0;
    }
    else if (p.position.x > 1.0)
    {
        p.position.x = -1.0;
    }

    if (p.position.y < -1.0)
    {
        p.position.y = 1.0;
    }
    push_pressure(p);

    vec2 cursor_delta = p.position.xy - u_cursor.xy;
    float d = length(cursor_delta);

    p.velocity.xy += cursor_delta * p.cursor_bound;

    p.cursor_bound *= 0.94;
    p.cursor_bound += smoothstep(0.2, 0.0, d) * 0.0003;

    p.velocity.x += (random(local_id) * 2.0 - 1.0) * 0.000023;

    p.velocity *= 0.93;
    p.velocity.y -= 0.0098 / 3600.0;

    b_particles[i] = p;
}
