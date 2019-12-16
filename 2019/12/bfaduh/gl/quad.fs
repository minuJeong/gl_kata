#version 460
#define NEAR 0.02
#define FAR 100.0

in vec4 vs_pos;

out vec4 fs_colour;

uniform vec3 u_camerapos;
uniform float u_time;
uniform float u_aspect;

const vec3 UP = vec3(0.0, 1.0, 0.0);


struct Marching
{
    float T;
    vec3 P;
    vec3 base_color;
    float roughness;
    vec3 spec_color;
};

float sdf_floor(vec3 p, vec3 n)
{
    return dot(p, n);
}

float sdf_sphere(vec3 p, float r)
{
    return length(p) - r;
}

float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    vec3 d0 = max(d, 0.0);
    vec3 d1 = min(d, 0.0);
    return length(d0) + max(d1.x, max(d1.y, d1.z));
}

float op_union_round(float a, float b, float t)
{
    vec2 u = max(vec2(t - a, t - b), 0.0);
    return max(t, min(a, b)) - length(u);
}

float sdf_world(vec3 p, inout Marching m)
{
    m.base_color = vec3(0.7, 0.8, 0.6);
    m.roughness = 1.0;
    m.spec_color = vec3(1.0);

    float dist = sdf_floor(p - vec3(0.0, -1.0, 0.0), UP);

    // sphere
    {
        float d = sdf_sphere(p - vec3(-1.0, cos(u_time * 4.0), -sin(u_time * 4.0) + 1.0), 1.0);

        m.base_color = mix(m.base_color, vec3(0.2, 0.4, 0.6), clamp((dist - d) * 0.25, 0.0, 1.0));
        if (d < NEAR)
        {
            m.roughness = 1.0;
        }

        dist = op_union_round(dist, d, 1.0);
    }

    // box
    {
        float boxsize = 0.95 * (cos(u_time * 2.4) * 0.2 + 0.8);
        float d = sdf_box(p - vec3(+1.0, 0.0, 0.0), vec3(boxsize)) - 0.05;

        m.base_color = mix(m.base_color, vec3(1.2, 0.3, 0.2), clamp((dist - d) * 0.25, 0.0, 1.0));
        if (d < NEAR)
        {
            m.roughness = 0.0;
        }

        dist = op_union_round(dist, d, 1.0);
    }

    // box 2
    {
        float boxsize = 0.8;
        float d = sdf_box(p - vec3(0.0, 0.2, -1.0), vec3(boxsize)) - 0.2;

        dist = max(dist, -d);
    }

    return dist;
}

void raymarch(vec3 o, vec3 r, inout Marching m)
{
    float d, t;
    vec3 p;
    for (int i = 0; i < 128; i++)
    {
        p = o + r * t;
        d = sdf_world(p, m);
        if (d < NEAR || t > FAR) {break;}
        t += d;
    }
    m.T = t;
    m.P = p;
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
    Marching _m;
    const vec2 e = vec2(0.002, 0.0);
    return normalize(sdf_world(p, _m) - vec3(
        sdf_world(p - e.xyy, _m),
        sdf_world(p - e.yxy, _m),
        sdf_world(p - e.yyx, _m)
    ));
}

void main()
{
    vec2 uv = vs_pos.xy;
    uv.x *= u_aspect;

    vec3 org = u_camerapos;
    float c, s;
    c = cos(u_time * 0.03);
    s = sin(u_time * 0.03);
    org.xz = mat2(c, -s, s, c) * org.xz;

    vec3 ray = lookzero(org) * normalize(vec3(uv, 1.0));
    vec3 light_pos = vec3(-10.0, 10.0, -10.0);

    Marching M;
    raymarch(org, ray, M);

    vec3 RGB;
    if (M.T < FAR)
    {
        vec3 P = M.P;
        vec3 N = normalat(P);
        vec3 L = normalize(light_pos - P);
        vec3 V = -ray;
        vec3 H = normalize(V + L);

        float spec = dot(N, H);
        spec = max(spec, 0.0);

        float spec_exp = 64.0;
        spec = pow(spec, spec_exp);

        float fresnel = 1.0 - dot(N, V);
        fresnel = max(fresnel, 0.0);
        fresnel = pow(fresnel, 5.0);
        spec += fresnel * 0.3;

        float diffuse = dot(N, L);
        diffuse += max(dot(N, -UP), 0.0) * 1.5;
        diffuse = max(diffuse, 0.0);

        float ambient = 1.0 - diffuse;

        vec3 light = spec * M.spec_color + diffuse * M.base_color + ambient * vec3(0.1, 0.1, 0.2);

        RGB = light;
    }

    RGB = clamp(RGB, 0.0, 1.0);
    fs_colour = vec4(RGB, 1.0);
}
