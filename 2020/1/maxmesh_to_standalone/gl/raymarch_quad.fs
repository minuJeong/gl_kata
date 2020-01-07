#version 460

#define NEAR 0.01
#define FAR 100.0

struct RM
{
    vec3 pos;
    float t;
};

in vec2 vs_pos;
out vec4 fs_color;

const vec3 UP = vec3(0.0, 1.0, 0.0);


float sdf_sphere(vec3 p, float radius)
{
    return length(p) - radius;
}

float sdf_world(inout RM m)
{
    vec3 p = m.pos;

    float d_sphere = sdf_sphere(p, 2.0);

    return d_sphere;
}

RM raymarch(vec3 o, vec3 r)
{
    RM res;
    float d;

    for (int i = 0; i < 128; i++)
    {
        res.pos = o + r * res.t;
        d = sdf_world(res);
        if (d < NEAR || res.t > FAR)
        {
            break;
        }
        res.t += d;
    }

    return res;
}

mat3 lookzero(vec3 o)
{
    vec3 f = normalize(-o);
    vec3 r = cross(f, UP);
    vec3 u = cross(r, f);
    return mat3(r, u, f);
}

vec3 normalat(vec3 p)
{
    const vec2 e = vec2(0.002, 0.0);
    RM r, rx, ry, rz;
    r.pos = p;
    rx.pos = p - e.xyy;
    ry.pos = p - e.yxy;
    rz.pos = p - e.yyx;
    return normalize(sdf_world(r) - vec3(
        sdf_world(rx),
        sdf_world(ry),
        sdf_world(rz)
    ));
}

void main()
{
    vec2 uv = vs_pos;

    vec3 org = vec3(-2.0, -2.0, -5.0);
    vec3 ray = lookzero(org) * normalize(vec3(uv, 1.0));
    vec3 RGB;
    RGB = vec3(0.1 - uv.y * 0.1);

    RM r = raymarch(org, ray);

    if (r.t < FAR)
    {
        const vec3 light_pos = vec3(5.0, 10.0, -32.0);

        vec3 P = r.pos;
        vec3 N = normalat(P);
        vec3 L = normalize(light_pos - P);

        float lambert = dot(N, L);

        RGB = lambert.xxx;
    }

    fs_color = vec4(RGB, 1.0);
}
