#version 460

in vec2 vs_pos;
out vec4 fs_color;

uniform float u_aspect;
uniform float u_time;
layout(location=0) uniform sampler2D u_texture;

struct Material
{
    vec3 base_color;
};

const vec3 ZERO = vec3(0.0);
const vec3 UP = vec3(0.0, 1.0, 0.0);

float sdf_sphere(vec3 p, float radius)
{
    return length(p) - radius;
}

float sdf_plane(vec3 p, vec3 n)
{
    return dot(p, n);
}

float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    vec3 d0 = max(d, 0.0);
    vec3 d1 = min(d, 0.0);
    return length(d0) + max(d1.x, max(d1.y, d1.z));
}


float op_smooth_union( float d1, float d2, float k )
{
    float h = clamp( 0.5 + 0.5*(d2-d1)/k, 0.0, 1.0 );
    return mix( d2, d1, h ) - k*h*(1.0-h);
}

// http://mercury.sexy/hg_sdf/
float op_union_stairs(float a, float b, float r, float n)
{
    float s = r/n;
    float u = b-r;
    return min(min(a,b), 0.5 * (u + a + abs ((mod (u - a + s, 2 * s)) - s)));
}

// https://www.iquilezles.org/www/articles/distfunctions/distfunctions.htm
float sdf_world(vec3 p, inout Material M)
{
    float dist;
    M.base_color = vec3(0.0, 0.0, 1.0);

    // plane
    {
        vec3 q = p;
        q.y += 0.5;
        float d = sdf_plane(q, UP);

        dist = d;
    }

    // sphere
    {
        vec3 q = p;
        q.x -= 1.0;
        q.y += pow(cos(u_time * 4.0) * 0.5 + 0.5, 8.0) * -2.0;
        float d = sdf_sphere(q, 1.0);

        float t = dist - d - 0.5;
        t = clamp(t, 0.0, 1.0);
        M.base_color = mix(M.base_color, vec3(1.0, 0.0, 0.0), t);

        dist = op_smooth_union(dist, d, 0.5);
    }

    // box
    {
        vec3 q = p;
        q.x += 1.0;
        float d = sdf_box(q, vec3(0.8)) - 0.2;

        vec4 texcolor = texture(u_texture, q.xy * 0.7) + texture(u_texture, q.xz);

        float t = dist - d - 0.5;
        t = clamp(t, 0.0, 1.0);
        M.base_color = mix(M.base_color, texcolor.xyz, t);

        dist = op_smooth_union(dist, d, 0.5);
    }

    return dist;
}

float raymarch(vec3 o, vec3 r, inout Material M)
{
    float d, t;
    vec3 p;
    for (int i = 0; i < 128; i++)
    {
        p = o + r * t;
        d = sdf_world(p, M);
        if (d < 0.002 || t > 100.0) { break; }
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
    Material _m;
    const vec2 e = vec2(0.002, 0.0);
    return normalize(sdf_world(p, _m) - vec3(
        sdf_world(p - e.xyy, _m), sdf_world(p - e.yxy, _m), sdf_world(p - e.yyx, _m)
    ));

}

void main()
{
    vec2 uv = vs_pos;
    uv.x *= u_aspect;

    vec3 RGB = vec3(0.0);

    vec3 org = vec3(0.0, 3.0, -4.0);
    org.x = cos(u_time) * 5.0;
    org.z = sin(u_time) * 5.0;

    vec3 ray = lookat(org, vec3(0.0, 1.0, 0.0)) * normalize(vec3(uv, 1.0));
    vec3 light_pos = vec3(20.0, 50.0, -10.0);

    Material M;

    float travel = raymarch(org, ray, M);

    if (travel < 100.0)
    {
        vec3 P = org + ray * travel;
        vec3 N = normalat(P);
        vec3 L = normalize(light_pos - P);
        vec3 V = -ray;

        float lambert = dot(N, L);
        lambert = max(lambert, 0.0);

        float fresnel = 1.0 - dot(N, V);
        fresnel = max(fresnel, 0.0);
        fresnel = pow(fresnel, 5.0);
        fresnel *= 0.5;

        float attenuation = lambert + fresnel;

        RGB = attenuation * M.base_color;
    }

    fs_color = vec4(RGB, 1.0);
}
