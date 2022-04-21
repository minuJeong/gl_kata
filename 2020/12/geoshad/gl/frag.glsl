#version 460

#define NEAR 0.01
#define FAR 100.0

in vec4 vs_pos;
out vec4 fs_color;

uniform vec2 u_resolution;


float sdf_world(vec3 p)
{
    return length(p) - 2.0;
}

float march(vec3 o, vec3 r)
{
    vec3 p;
    float d, t;
    for (int i = 0; i < 64; i++)
    {
        p = o + r * t;
        d = sdf_world(p);
        if (d < NEAR || d > FAR)
        {
            break;
        }
        t += d;
    }
    return t;
}

mat3 lookat(vec3 p)
{
    vec3 f = normalize(-p);
    vec3 r = cross(f, vec3(0.0, 1.0, 0.0));
    vec3 u = cross(r, f);
    return mat3(r, u, f);
}

vec3 normalat(vec3 p)
{
    const vec2 e = vec2(0.0, 0.02);
    return normalize(sdf_world(p) - vec3(
        sdf_world(p - e.xyy),
        sdf_world(p - e.yxy),
        sdf_world(p - e.yyx)
    ));
}

void main()
{
    vec2 uv = vs_pos.xy;
    uv.x /= u_resolution.y / u_resolution.x;

    vec3 rgb = vec3(0.11 - (uv.y * 0.06));

    vec3 org = vec3(-2.0, 2.0, -5.0);
    vec3 ray = lookat(org) * normalize(vec3(uv, 1.0));

    float travel = march(org, ray);
    if (travel < FAR)
    {
        vec3 P = org + ray * travel;
        vec3 N = normalat(P);
        rgb = N;
    }

    fs_color = vec4(rgb, 1.0);
}
