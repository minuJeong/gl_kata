#version 460

#define NEAR 0.001
#define FAR 100.0

in vec2 vs_pos;
out vec4 fs_color;

uniform float u_time;

struct March
{
    float travel;
    vec3 pos;
    vec3 color;
};

const vec3 ZERO = vec3(0.0, 0.0, 0.0);
const vec3 UP = vec3(0.0, 1.0, 0.0);

mat3 lookat(vec3 pos, vec3 at)
{
    vec3 f = normalize(at - pos);
    vec3 r = cross(f, UP);
    vec3 u = cross(r, f);
    return mat3(r, u, f);
}

float sdf_sphere(vec3 pos, float radius)
{
    return length(pos) - radius;
}

float sdf_plane(vec3 pos, vec3 n, float d)
{
    return dot(pos, n) - d;
}

float sdf_box(vec3 pos, vec3 box)
{
    vec3 b = abs(pos) - box;
    vec3 b0 = max(b, 0.0);
    vec3 b1 = min(b, 0.0);
    return length(b0) - max(b1.x, max(b1.y, b1.z));
}

bool isinbox(vec3 p, vec3 box)
{
    return sdf_box(p, box) < 0.0;
}

float sdf_world(inout March march)
{
    vec3 pos = march.pos;

    float d_plane = sdf_plane(pos, UP, -2.0);
    march.color = vec3(0.8, 0.3, 0.2);

    float d_scene = d_plane;
    {
        float d_sphere = sdf_sphere(pos - vec3(-1.0, 0.0, 0.0), 1.0);
        float d_box = sdf_box(pos - vec3(+1.0, 0.0, 0.0), vec3(0.9)) - 0.1;

        march.color = mix(march.color, vec3(0.12, 0.3, 0.8), clamp(d_box - d_sphere, 0.0, 1.0));
        march.color = mix(march.color, vec3(0.2, 0.76, 0.1), clamp(d_sphere - d_plane, 0.0, 1.0));

        d_scene = min(d_box, d_sphere);
    }

    return min(d_scene, d_plane);
}

bool raymarch(vec3 o, vec3 r, inout March march)
{
    march.pos = o + r * 3.0;
    march.travel = sdf_world(march);
    float d, i; for (i = 0; i < 24; i++)
    {
        march.pos = o + r * march.travel;
        d = sdf_world(march);
        if (d < NEAR || march.travel > FAR) { break; }
        march.travel += d;
    }
    return march.travel < FAR;
}

vec3 normalat(vec3 pos)
{
    const vec2 e = vec2(NEAR, 0.0);

    March march;
    March marchx;
    March marchy;
    March marchz;
    march.pos = pos;
    marchx.pos = pos - e.xyy;
    marchy.pos = pos - e.yxy;
    marchz.pos = pos - e.yyx;
    return normalize(sdf_world(march) - vec3(
        sdf_world(marchx),
        sdf_world(marchy),
        sdf_world(marchz)
    ));
}

void main()
{
    vec2 uv = vs_pos.xy;

    vec3 pos = vec3(-5.0, 2.0, -5.0);
    pos.x = cos(u_time) * 5.0;
    pos.z = sin(u_time) * 5.0;
    vec3 ray = lookat(pos, ZERO) * normalize(vec3(uv, 1.0));

    March march;
    vec3 RGB = vec3(0.2 - uv.y * 0.2);
    if (raymarch(pos, ray, march)) {}
    {
        vec3 P = march.pos;
        vec3 N = normalat(P);
        vec3 L = normalize(vec3(-10.0, 10.0, -5.0) - P);
        vec3 V = -ray;

        float fresnel = 1.0 - dot(N, V);
        fresnel = pow(max(fresnel, 0.0), 3.0);
        fresnel *= 0.1;
        float specular = fresnel;
        vec3 spec_color = vec3(1.0, 0.8, 0.8) * specular;

        float lambert = (1.0 - specular) * dot(N, L);
        lambert = clamp(lambert, 0.0, 1.0);
        vec3 diffuse_color = march.color * lambert;

        float ambient = 1.0 - lambert;
        ambient *= 0.2;
        ambient = max(ambient, 0.0);

        vec3 ambient_color = vec3(0.4, 0.2, 0.5) * ambient;

        RGB = spec_color + diffuse_color + ambient_color;
    }
    fs_color = vec4(clamp(RGB, 0.0, 1.0), 1.0);
}
