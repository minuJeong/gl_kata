#version 460

#define NEAR 0.0002
#define FAR 100.0

in vec2 vs_pos;
out vec4 fs_color;

uniform vec2 u_resolution;
uniform float u_time;


float sphere(vec3 p, float r)
{
    return length(p) - r;
}

float world(vec3 p)
{
    const float SQUASH = cos(u_time * 8.2);
    const float SQUASH_AMOUNT = 0.08;
    p.y = p.y + p.y * SQUASH * SQUASH_AMOUNT;
    p.x = p.x + p.x * (1.0 - SQUASH) * SQUASH_AMOUNT;

    float d = sphere(p, 2.0);

    float c = cos(u_time);
    float s = sin(u_time);
    p.xz = mat2(c, -s, s, c) * p.xz;
    p.yz = mat2(c, -s, s, c) * p.yz;

    const float DISPLACEMENT = cos(u_time * 1.6) * 8.7;
    const float DISPLACEMENT_AMOUNT = cos(u_time) * 0.06 + 0.12;
    vec3 disp = cos(p * DISPLACEMENT) * DISPLACEMENT_AMOUNT;

    d += length(disp);

    return d;
}

float raymarch(vec3 o, vec3 r)
{
    vec3 p;
    float t;
    float d;

    for (int i = 0; i < 32; i++)
    {
        p = o + r * t;
        d = world(p);

        if (d < NEAR || t > FAR)
        {
            break;
        }
        t += d;
    }

    return t;
}

vec3 normal_at(vec3 p)
{
    const vec2 e = vec2(NEAR, 0.0);
    return normalize(vec3(
        world(p + e.xyy) - world(p - e.xyy),
        world(p + e.yxy) - world(p - e.yxy),
        world(p + e.yyx) - world(p - e.yyx)
    ));
}

void main()
{
    vec2 uv = vs_pos;
    float aspect = u_resolution.x / u_resolution.y;
    uv.x *= aspect;

    vec3 o = vec3(0.0, 0.0, -5.0);
    vec3 r = normalize(vec3(uv, 1.0));

    vec3 RGB = vec3(uv.y * 0.1 + 0.15);

    float t = raymarch(o, r);
    if (t < FAR)
    {
        vec3 P = o + r * t;
        vec3 N = normal_at(P);
        vec3 L = normalize(vec3(-5.0, 5.0, -5.0) - P);

        float lambert = dot(N, L) * 0.7 + 0.3;
        
        RGB = vec3(lambert);
    }

    fs_color = vec4(RGB, 1.0);
}
