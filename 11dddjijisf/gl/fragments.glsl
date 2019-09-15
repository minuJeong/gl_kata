#version 460

#define NEAR 0.002
#define FAR 100.0

#include ./gl/hg_sdf.glsl

struct RaymarchData
{
    float travel;
    vec3 pos;
};

in vec3 vs_pos;
in vec2 vs_uv;

out vec4 fs_color;

uniform float u_time;

float world(inout RaymarchData r)
{
    vec3 pos = r.pos;

    vec3 j1 = vec3(0.0);
    j1.y = cos(u_time * 4.0) * 0.25;
    float dist_sphere = fSphere(pos - j1, 2.0);
    return dist_sphere;
}

float world_pos(vec3 p)
{
    RaymarchData raymarch;
    raymarch.pos = p;
    return world(raymarch);
}

RaymarchData raymarch(vec3 o, vec3 r)
{
    RaymarchData res;

    float d;
    for (int i = 0; i < 32; i++)
    {
        res.pos = o + r * res.travel;
        d = world(res);
        if (d < NEAR || res.travel > FAR)
        {
            break;
        }
        res.travel += d;
    }

    return res;
}

vec3 normal_at(vec3 p)
{
    const vec2 e = vec2(0.002, 0.0);
    return normalize(vec3(
        world_pos(p + e.xyy) - world_pos(p - e.xyy),
        world_pos(p + e.yxy) - world_pos(p - e.yxy),
        world_pos(p + e.yyx) - world_pos(p - e.yyx)
    ));
}

void main()
{
    vec3 o = vec3(0.0, 0.0, -5.0);
    vec3 r = normalize(vec3(vs_uv * 2.0 - 1.0, 1.0));

    vec3 RGB = vec3(0.0);
    RaymarchData res = raymarch(o, r);

    vec3 P = o + r * res.travel;
    vec3 N = normal_at(P);

    float lambert = dot(N, vec3(-2.0, 2.0, -2.0)) * 0.5 + 0.5;
    lambert += 0.2;
    RGB = max(saturate(lambert), 0.2).xxx;

    // fs_color = vec4(RGB, 1.0);
    fs_color = vec4(vs_uv, 0.0, 1.0);
}
