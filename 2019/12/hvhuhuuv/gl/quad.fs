#version 460
#define NEAR 0.002
#define FAR 100.0

in vec4 vs_pos;
out vec4 fs_colour;

struct MRes
{
    float T;
    vec3 P;
};

uniform vec4 u_camerapos = vec4(1.0, 1.0, -5.0, 1.0);
uniform float u_time;
uniform float u_aspect;

const vec3 UP = vec3(0.0, 1.0, 0.0);

float vmax(vec2 uv) { return max(uv.x, uv.y); }
float vmax(vec3 uvw) { return max(uvw.x, vmax(uvw.yz)); }
float vmax(vec4 xyzw) { return max(vmax(xyzw.xy), vmax(xyzw.zw)); }

#define sdf_point(x) length(x)

float sdf_sphere(vec3 p, float rad)
{
    return sdf_point(p) - rad;
}

float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    vec3 d0 = max(d, 0.0);
    vec3 d1 = min(d, 0.0);
    return length(d0) + vmax(d1);
}

float sdf_plane(vec3 p, vec3 n)
{
    return dot(p, n);
}

float sdf_world(vec3 p, inout MRes res)
{
    float distance = sdf_plane(p - vec3(0.0, -10.0, 0.0), UP);
    {
        vec3 q = p;

        float d1 = sdf_sphere(q, 5.0);
        float d2 = sdf_box(q, vec3(3.5)) - 1.5;
        // float d = mix(d1, d2, cos(u_time * 0.4) * 0.5 + 0.5);
        float d = d1;

        distance = min(d, distance);
    }

    return distance;
}

void march(vec3 o, vec3 r, inout MRes res)
{
    float t, d;
    vec3 p;
    for (int i = 0; i < 128; i++)
    {
        p = o + r * t;
        d = sdf_world(p, res);
        if (d < NEAR || t > FAR) { break; }
        t += d;
    }
    res.T = t;
    res.P = p;
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
    MRes m;
    const vec2 e = vec2(NEAR, 0.0);
    return normalize(sdf_world(p, m) - vec3(
        sdf_world(p - e.xyy, m),
        sdf_world(p - e.yxy, m),
        sdf_world(p - e.yyx, m)
    ));
}

void main()
{
    vec2 uv = vs_pos.xy;
    uv.x *= u_aspect;

    vec3 org = u_camerapos.xyz;
    vec3 ray = lookzero(org) * normalize(vec3(uv, 1.0));
    vec3 light_pos = vec3(-20.0, 30.0, 65.0);

    MRes res;
    march(org, ray, res);

    vec3 RGB;
    if (res.T < FAR)
    {
        vec3 P = res.P;
        vec3 N = normalat(P);
        vec3 L = normalize(light_pos - P);
        vec3 V = -ray;
        vec3 H = normalize(L + V);

        float diffuse = dot(N, L);
        diffuse = smoothstep(0.23, 0.33, diffuse);
        diffuse = max(diffuse, 0.2);

        float spec = dot(N, H);
        spec = max(spec, 0.0);
        spec = pow(spec, 32.0);
        spec = smoothstep(0.77, 0.78, spec);

        float fresnel = 1.0 - max(dot(N, V), 0.0);
        fresnel = pow(fresnel, 5.0);
        fresnel = smoothstep(0.23, 0.25, fresnel);
        fresnel *= 0.8;

        RGB = (diffuse + spec + fresnel) * vec3(0.3, 0.4, 0.7);
    }

    RGB = clamp(RGB, 0.0, 1.0);
    fs_colour = vec4(RGB, 1.0);
}
