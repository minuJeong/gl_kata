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

float sdf_world(inout March march)
{
    vec3 pos = march.pos;
    float d_sphere = sdf_sphere(pos, 2.0);

    if (d_sphere < FAR)
    {
        march.color = vec3(0.8, 0.3, 0.2);
    }

    return d_sphere;
}

bool raymarch(vec3 o, vec3 r, inout March march)
{
    float d;
    for (int i = 0; i < 24; i++)
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

        float lambert = dot(N, L);
        lambert = max(lambert, 0.0);
        vec3 diffuse_color = march.color * lambert;

        float ambient = 1.0 - lambert;
        ambient *= 0.1;
        ambient = clamp(ambient, 0.0, 1.0);
        vec3 ambient_color = vec3(0.2, 0.1, 0.7) * ambient;

        float light = lambert + ambient;

        RGB = vec3(light);
    }
    fs_color = vec4(RGB, 1.0);
}
