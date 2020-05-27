#version 460

#define ZERO vec3(0.0, 0.0, 0.0)
#define UP vec3(0.0, 1.0, 0.0)

in vec4 vs_pos;
out vec4 fs_color;

uniform float u_time;

float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    vec3 d0 = max(d, 0.0);
    vec3 d1 = min(d, 0.0);
    return length(d0) + max(d1.x, max(d1.y, d1.z));
}

float sdf_gyroid(vec3 p, float scale)
{
    p *= scale;
    float d = dot(cos(p), sin(p)) / scale;
    return d;
}

float sdf_world(vec3 p)
{
    float d = sdf_box(p, vec3(1.3));
    d -= 0.2;

    // float d = sdf_gyroid(p, 10.0);
    return d;
}

float march(vec3 o, vec3 r)
{
    vec3 p;
    float d, t;
    for (int i = 0; i < 256; i++)
    {
        p = o + r * t;
        d = sdf_world(p);
        if (d < 0.001 || t > 100.0) { break; }
        t += d;
    }
    return t;
}

mat3 lookat(vec3 o, vec3 t)
{
    vec3 f = normalize(t - o);
    vec3 r = cross(f, UP);
    vec3 u = cross(r, f);
    return mat3(r, u, f);
}

vec3 normalat(vec3 p)
{
    const vec2 e = vec2(0.02, 0.0);
    return normalize(sdf_world(p) - vec3(
        sdf_world(p - e.xyy),
        sdf_world(p - e.yxy),
        sdf_world(p - e.yyx)
    ));
}

void main()
{
    vec2 uv = vs_pos.xy;
    vec3 rgb = vec3(0.0, 0.0, 0.0);

    vec3 o = vec3(
        cos(u_time * 2.0) * 6.0,
        4.0,
        sin(u_time * 2.0) * 6.0
    );
    vec3 r = lookat(o, ZERO) * normalize(vec3(uv, 1.0));

    float d = march(o, r);
    if (d < 100.0)
    {
        vec3 p = o + r * d;
        vec3 n = normalat(p);

        float lambert = dot(n, normalize(vec3(1, 2, 3)));
        lambert = max(lambert, 0.1);
        rgb = lambert.xxx;
    }

    fs_color = vec4(rgb, 1.0);
}
