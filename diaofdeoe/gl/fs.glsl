#version 460

#define FAR 100.0

in vec2 vs_uv;

out vec4 fs_color;

uniform float u_time;


float sphere(vec3 p, float r)
{
    return length(p) - r;
}

float world(vec3 p)
{
    float d = FAR;
    {
        float SPD = 10.0;
        vec3 j1 = vec3(cos(u_time * SPD), sin(u_time * SPD), 0.0);
        float r1 = 2.0;

        float d1 = sphere(p - j1, r1);
        d = min(d1, d);
    }

    return d;
}

float raymarch(vec3 o, vec3 r)
{
    float t;
    float d;
    vec3 p;

    for (int i = 0; i < 64; i++)
    {
        p = o + r * t;
        d = world(p);

        if (d < 0.001 || t > FAR)
        {
            break;
        }

        t += d;
    }
    return t;
}

vec3 normal_at(vec3 p)
{
    vec2 e = vec2(0.1, 0.0);
    return normalize(vec3(
        world(p + e.xyy) - world(p - e.xyy),
        world(p + e.yxy) - world(p - e.yxy),
        world(p + e.yyx) - world(p - e.yyx)
    ));
}

void main()
{
    vec2 uv = vs_uv * 0.5 + 0.5;

    vec3 o = vec3(0.0, 0.0, -5.0);
    vec3 r = normalize(vec3(uv * 2.0 - 1.0, 1.0));

    float t = raymarch(o, r);
    vec3 rgb = vec3(0.2, 0.2, 0.2);
    if (t < FAR)
    {
        vec3 P = o + r * t;
        vec3 N = normal_at(P);
        vec3 L = normalize(vec3(-4.0, 5.0, -5.0) - P);

        float lambert = max(dot(N, L), 0.0);

        rgb = vec3(lambert, lambert, lambert);
    }

    fs_color = vec4(rgb, 1.0);
}
