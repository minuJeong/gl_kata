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

void cage_if(inout vec3 pos, inout vec3 vel)
{
    const float SIZE = 4.0;
    const float BOUNCE = 0.94;
    const float INERTIA = 0.94;

    vec3 bbox_min = vec3(-SIZE, -SIZE, -SIZE);
    vec3 bbox_max = vec3(+SIZE, +SIZE, +SIZE);

    if (pos.x < bbox_min.x || pos.x > bbox_max.x)
    {
        vel.x *= -BOUNCE + (hash12(vel.yz) * 0.1);
    }

    if (pos.y < bbox_min.y || pos.y > bbox_max.y)
    {
        vel.y *= -BOUNCE + (hash12(vel.xz) * 0.1);
    }

    if (pos.z < bbox_min.z || pos.z > bbox_max.z)
    {
        vel.z *= -BOUNCE + (hash12(vel.xy) * 0.1);
    }
    pos = min(max(pos, bbox_min), bbox_max);
}

void main()
{
    uvec3 uvw = gl_LocalInvocationID.xyz + gl_WorkGroupID.xyz * gl_WorkGroupSize.xyz;
    vec3 xyz = vec3(uvw.xyz);
    int i = int(xyz.x * 4 * 4 + xyz.y * 4 + xyz.z);

    Particle particle = particles[i];
    particle.position += particle.velocity * u_deltatime;
    vec3 pos = particle.position.xyz;
    vec3 vel = particle.velocity.xyz;

    cage_if(pos, vel);
    vel.y -= 0.005;

    particle.position.xyz = pos.xyz;
    particle.velocity.xyz = vel.xyz;

    particles[i] = particle;
}
