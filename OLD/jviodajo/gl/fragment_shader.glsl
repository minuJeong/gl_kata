#version 450

#include ./gl/hg_sdf.glsl

#define NEAR 0.02
#define FAR 50.0

in vec4 vs_pos;
in vec2 vs_uv0;

out vec4 fs_color;

uniform vec2 u_resolution;
uniform float u_time;

struct Material
{
    vec3 color;
};

float mod289(float x){return x - floor(x * (1.0 / 289.0)) * 289.0;}
vec4 mod289(vec4 x){return x - floor(x * (1.0 / 289.0)) * 289.0;}
vec4 perm(vec4 x){return mod289(((x * 34.0) + 1.0) * x);}

float noise(vec3 p){
    vec3 a = floor(p);
    vec3 d = p - a;
    d = d * d * (3.0 - 2.0 * d);

    vec4 b = a.xxyy + vec4(0.0, 1.0, 0.0, 1.0);
    vec4 k1 = perm(b.xyxy);
    vec4 k2 = perm(k1.xyxy + b.zzww);

    vec4 c = k2 + a.zzzz;
    vec4 k3 = perm(c);
    vec4 k4 = perm(c + 1.0);

    vec4 o1 = fract(k3 * (1.0 / 41.0));
    vec4 o2 = fract(k4 * (1.0 / 41.0));

    vec4 o3 = o2 * d.z + o1 * (1.0 - d.z);
    vec2 o4 = o3.yw * d.x + o3.xz * (1.0 - d.x);

    return o4.y * d.y + o4.x * (1.0 - d.y);
}

float world(vec3 p, inout Material material)
{
    // base sdf
    vec3 sp0_space = p;
    vec3 sp0_pos = sp0_space - vec3(
        cos(u_time * 2.14) * 2.0,
        sin(u_time * 2.14) * 2.0,
        0.0);
    pR(sp0_pos.yz, mod(u_time * 3.0, 3.14));
    float d_icosahedron = fIcosahedron(sp0_pos, 2.2);

    vec3 box0_space = p;
    vec3 box0_pos = box0_space - vec3(
        sin(u_time * 2.4) * 0.8,
        0.0,
        cos(u_time * 2.4) * 0.8);
    vec3 box0_size = vec3(1.0, 2.0, 1.0);

    float box0_rotation_amount = mod(u_time * 2.4, 3.14);
    float box0_rotation = box0_rotation_amount;

    pR(box0_pos.yz, -box0_rotation);

    float d_box = fBox(box0_pos, box0_size);

    // mix shapes
    float mixer = cos(u_time * 0.3) * 0.5 + 0.5;
    float d = mix(d_icosahedron, d_box, mixer);
    material.color = mix(vec3(1.0, 0.0, 0.0), vec3(0.0, 0.0, 1.0), mixer);

    return d;
}

float raymarch(vec3 o, vec3 r, inout Material material)
{
    float d, t;
    vec3 p;
    for (int i = 48; i > 0; i--)
    {
        p = o + r * t;
        d = world(p, material);
        if (d < NEAR || t > FAR)
        {
            break;
        }
        t += d;
    }
    return t;
}

vec3 normal_at(vec3 p)
{
    const vec2 e = vec2(0.002, 0.0);
    Material material;
    return normalize(vec3(
        world(p + e.xyy, material) - world(p - e.xyy, material),
        world(p + e.yxy, material) - world(p - e.yxy, material),
        world(p + e.yyx, material) - world(p - e.yyx, material)
    ));
}

float calc_alpha(vec3 p, vec3 r)
{
    Material material;

    float d;
    float t = 0.0;

    float alpha = 0.0;
    for (int i = 64; i > 0; i--)
    {
        t = world(p + r * d, material);
        alpha += t < 0.0 ? 0.014 : 0.0;
        d += 0.095;
    }
    return saturate(alpha);
}

void main()
{
    vec3 RGB = vec3((1.0 - vs_uv0.yyy) * 0.15 + 0.05);
    float alpha = 0.0;

    vec2 cuv = vs_pos.xy;
    cuv.x *= u_resolution.x / u_resolution.y;

    vec3 o = vec3(0.0, 0.0, -5.0);
    vec3 r = normalize(vec3(cuv, 1.0));
    Material material;

    float t = raymarch(o, r, material);

    vec3 sceneRGB = RGB;
    if (t < FAR)
    {
        vec3 P = o + r * t;
        vec3 N = normal_at(P);
        vec3 L = normalize(vec3(-3.0, 4.0, -5.0) - P);

        sceneRGB = dot(N, L) * 0.5 + 0.5 * material.color;
        alpha = calc_alpha(P, r);
    }

    RGB = saturate(mix(RGB, sceneRGB, alpha));
    fs_color = vec4(RGB, alpha);
}
