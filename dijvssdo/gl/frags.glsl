#version 460
#include ./gl/hg_sdf.glsl

#define NEAR 0.2
#define FAR 50.0

in vec2 vs_pos;
in vec2 vs_uv;

out vec4 fs_color;

float scene(vec3 p)
{
    float d;

    {
        vec3 sphere_pos = vec3(0.0, 0.0, 0.0);
        float sphere_radius = 2.0;
        float dist_sphere = fSphere(p - sphere_pos, sphere_radius);

        d = dist_sphere;
    }

    return d;
}

float raymarch(vec3 o, vec3 r)
{
    vec3 p;
    float d;
    float t;

    for (int i = 0; i < 48; i++)
    {
        p = o + r * t;
        d = scene(p);
        if (d < NEAR || t > FAR)
        {
            break;
        }

        t += d;
    }
    return t;
}

void main()
{
    vec3 o = vec3(0.0, 0.0, -5.0);
    vec3 r = normalize(vec3(vs_pos, 1.0));

    float distance = raymarch(o, r);

    fs_color = vec4(vs_uv, distance / FAR, 1.0);
}
