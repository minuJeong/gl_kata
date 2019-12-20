#version 460

in vec2 vs_pos;
out vec4 fs_color;

const vec3 UP = vec3(0.0, 1.0, 0.0);


float sdf_sphere(vec3 p, float radius)
{
    return length(p) - radius;
}

float world(vec3 p)
{
    return sdf_sphere(p, 2.0);
}

float raymarch(vec3 o, vec3 r)
{
    float d, t;
    vec3 p;
    for (int i = 0; i < 48; i++)
    {
        p = o + r * t;
        d = world(p);
        if (d < 0.002 || t > 100.0)
        {
            break;
        }
        t += d;
    }
    return t;
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
    return normalize(world(p) - vec3(
        world(p - e.xyy),
        world(p - e.yxy),
        world(p - e.yyx)
    ));
}

void main()
{
    vec2 uv = vs_pos;
    vec3 RGB = vec3(uv, 0.5);

    vec3 org = vec3(-4.0, 4.0, -6.0);
    vec3 ray = lookzero(org) * normalize(vec3(uv, 1.0));
    vec3 lightpos = vec3(100.0, 100.0, -100.0);

    float t = raymarch(org, ray);
    if (t < 100.0)
    {
        vec3 P = org + ray * t;
        vec3 N = normalat(P);
        vec3 L = normalize(lightpos - P);

        RGB = max(dot(N, L), 0.0) * vec3(1.0);
    }

    fs_color = vec4(RGB, 1.0);
}
