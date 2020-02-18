#version 460

in vec2 vs_pos;
out vec4 fs_colour;

layout(binding=0) buffer CONSTANTS
{
    float u_time;
};

const vec3 ZERO = vec3(0.0, 0.0, 0.0);
const vec3 UP = vec3(0.0, 1.0, 0.0);

mat3 lookat(vec3 o, vec3 t)
{
    vec3 f = normalize(t - o);
    vec3 r = cross(f, UP);
    vec3 u = cross(r, f);
    return mat3(r, u, f);
}

float sdf_sphere(vec3 p, float radius) { return length(p) - radius; }
float sdf_cube(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    vec3 d0 = max(d, 0.0);
    vec3 d1 = min(d, 0.0);
    return length(d0) - max(d1.x, max(d1.y, d1.z));
}

float sdf_world(vec3 p)
{
    vec3 q = p;
    float c = cos(u_time), s = sin(u_time);
    q.x += cos(u_time * 2.0);
    q.xz = mat2(c, -s, s, c) * q.xz;
    float dist_cube = sdf_cube(q, vec3(1.0)) - 0.25;
    float dist_sphere = sdf_sphere(p, 1.5);

    return mix(dist_cube, dist_sphere, cos(u_time) * 0.5 + 0.5);
}

float march(vec3 o, vec3 r)
{
    float d, t = 2.0;
    vec3 p;
    for (int i = 0; i < 64; i++)
    {
        p = o + r * t;
        d = sdf_world(p);
        if (d < 0.001 || t > 100.0) {break;}
        t += d;
    }
    return t;
}

vec3 normalat(vec3 p)
{
    const vec2 e = vec2(0.001, 0.0);
    return normalize(sdf_world(p) - vec3(
        sdf_world(p - e.xyy),
        sdf_world(p - e.yxy),
        sdf_world(p - e.yyx)
    ));
}

void main()
{
    vec2 uv = vs_pos.xy;

    vec3 campos = vec3(-2.0, 4.0, -6.0);

    vec3 ray = lookat(campos, ZERO) * normalize(vec3(uv, 1.0));
    vec3 light_pos = vec3(cos(u_time) * 5.0, 5.0, sin(u_time) * 5.0);
    vec3 colour = 0.2 - uv.yyy * 0.1;

    float t = march(campos, ray);
    if (t < 100.0)
    {
        vec3 P = campos + t * ray;
        vec3 N = normalat(P);
        vec3 L = normalize(light_pos - P);

        float lambert = dot(N, L);

        colour = lambert.xxx;
    }

    fs_colour = vec4(colour, 1.0);
}
