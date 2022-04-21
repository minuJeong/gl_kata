#version 460

in vec4 vs_pos;
out vec4 fs_color;

uniform vec2 u_resolution;
uniform float u_time;


float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    vec3 dn = min(d, vec3(0.0, 0.0, 0.0));
    return length(max(d, vec3(0.0, 0.0, 0.0))) + max(dn.x, max(dn.y, dn.z));
}


float sdf_sphere(vec3 p, float radius)
{
    return length(p) - radius;
}

float world(vec3 p)
{
    vec3 q = p - vec3(0.0, 0.0, 0.0);
    float c = cos(u_time * 4.0);
    float s = sin(u_time * 4.0);
    q.yz = mat2(c, -s, s, c) * q.yz;
    float ds_0 = sdf_box(q, vec3(0.95)) - 0.05;

    float ds_1 = sdf_sphere(p, 1.5);
    // ds_1 -= cos(p.x * 20.0) * cos(p.y * 20.0) * cos(p.z * 20.0) * 0.01;

    float d = mix(ds_0, ds_1, cos(u_time * 1.0) * 0.5 + 0.5);

    return d;
}


float raymarch(vec3 o, vec3 r)
{
    vec3 p;
    float d, t;

    for (int i = 0; i < 48; i++)
    {
        p = o + r * t;
        d = world(p);
        if (d < 0.01 || t > 100.0) { break; }
        t += d;
    }

    return t;
}

mat3 lookat(vec3 look_from)
{
    vec3 f = normalize(-look_from);
    vec3 r = cross(f, vec3(0.0, 1.0, 0.0));
    vec3 u = cross(r, f);

    return mat3(r, u, f);
}

vec3 normalat(vec3 pos)
{
    const vec2 e = vec2(0.002, 0.0);
    return normalize(world(pos) - vec3(
        world(pos - e.xyy),
        world(pos - e.yxy),
        world(pos - e.yyx)
    ));
}

void main()
{
    vec2 uv = vs_pos.xy;
    uv.x /= u_resolution.y / u_resolution.x;

    vec3 RGB = vec3(0.2 - uv.y * 0.1);

    vec3 origin = vec3(-2.0, 2.0, -5.0);
    origin.x = cos(u_time * 2.0) * 5.0;
    origin.z = sin(u_time * 2.0) * 5.0;

    vec3 ray = lookat(origin) * normalize(vec3(uv, 1.0));

    float travel = raymarch(origin, ray);

    if (travel < 100.0)
    {
        const vec3 L = vec3(5.0, 5.0, 0.0);
        vec3 P = origin + ray * travel;
        vec3 N = normalat(P);

        float lambert = dot(N, normalize(L - P));
        lambert = clamp(lambert, 0.05, 1.0);

        RGB = lambert.xxx;
    }

    fs_color = vec4(RGB, 1.0);
}
