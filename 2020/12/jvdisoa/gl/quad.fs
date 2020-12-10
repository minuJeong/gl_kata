#version 460

#define NEAR 0.02
#define FAR 100.0
#define MARCHING_STEPS 44

in vec4 vs_pos;
out vec4 fs_color;

uniform float u_time;

struct Material
{
    vec3 albedo;
};

float hash(vec2 uv) { return fract(cos(dot(uv, vec2(12.312, 35.554))) * 43215.4); }
float hash(vec3 uvw) { return fract(cos(dot(uvw, vec3(12.312, 35.554, 332.344))) * 43215.4); }

float sdf_sphere(vec3 p, float rad)
{
    return length(p) - rad;
}

float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    vec3 d0 = max(d, vec3(0.0, 0.0, 0.0));
    vec3 d1 = min(d, vec3(0));
    return length(d0) + max(d1.x, max(d1.y, d1.z));
}
float sdf_box(vec3 p, float w, float h, float d) { return sdf_box(p, vec3(w, h, d)); }

float sdf_torus(vec3 p, float rad_0, float rad_2)
{
    return length(vec2(length(p.xz) - rad_2, p.y)) - rad_0;
}

float smin(float a, float b, float k)
{
    float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
    return mix(b, a, h) - k * h * (1.0 - h);
}

mat2 rot(float angle)
{
    float c = cos(angle), s = sin(angle);
    return mat2(c, s, -s, c);
}

float displacement(vec3 xyz, float step)
{
    return cos(xyz.x * step) * cos(xyz.y * step) * cos(xyz.z * step);
}

float sdf_world(vec3 p, inout Material material)
{
    float d_0;
    {
        vec3 sphere_offset = vec3(cos(u_time * 4.32) * 1.5 - 1.5, 0.0, sin(u_time * 4.32) * 1.5 - 1.5);
        const float sphere_radius = 2.25;
        const vec3 box_offset = vec3(-1.5, 0.0, 0.0);
        const vec3 box_size = vec3(2.0, 2.0, 2.0);
        const float box_round = 0.12;
        const float smooth_factor = 1.5;
        const float rotation_speed = 4.2;

        vec3 q = p;
        float d_sphere = sdf_sphere(q - sphere_offset, sphere_radius);
        q.yz = rot(u_time * rotation_speed) * q.yz;
        float d_box_0 = sdf_box(q - box_offset, box_size) - box_round;
        d_0 = smin(d_sphere, d_box_0, smooth_factor);
    }

    float d_1;
    {
        const float box_2_rotation_speed = -6.43;
        const float box_2_size = 2.15;
        const float box_2_round = 0.25;
        float displacement_amount = cos(u_time * 7.223) * 0.2;
        vec3 q = p;
        q.xz = rot(u_time * box_2_rotation_speed) * q.xz;
        float d_box_1 = sdf_box(q, vec3(box_2_size)) - box_2_round;
        d_box_1 += displacement(q * 0.8, 10.0) * displacement_amount;
        d_1 = d_box_1;
    }

    float d_2;
    {
        const float xy_rotation_speed = 0.132;
        const float torus_radius_min = 1.2;
        float torus_radius_max = cos(u_time * 8.432) * 0.2 + 3.2;
        vec3 q = p;
        q.xy = rot(u_time * xy_rotation_speed) * q.xy;
        float d = sdf_torus(q, torus_radius_min, torus_radius_max);

        vec3 q2 = q;
        q2.yz = rot(u_time * 4.4321) * q2.yz;
        d += displacement(q2, 1.0) * -0.3;
        d_2 = d;
    }

    float d_3;
    {
        const float elastic_timing_scale = 8.324;
        const float fracture_scale = 3.0;
        vec3 q = p;
        vec3 coord = floor(q * fracture_scale) / fracture_scale;
        float r = hash(coord);
        mat2 squeeze = rot(r * q.y * cos(u_time * elastic_timing_scale) * 0.03);
        q.xz = squeeze * q.xz;
        q.xy = squeeze * q.xy;
        q.yz = squeeze * q.yz;

        d_3 = sdf_box(q, 2.2, 2.2, 2.2) - 0.2;
    }

    const float max_time = 15.0;
    float t = mod(u_time, max_time);
    float t01 = smoothstep(0.0, 4.0, t);
    float t12 = smoothstep(4.0, 8.0, t);
    float t23 = smoothstep(8.0, 13.0, t);
    float t30 = smoothstep(13.0, 15.0, t);
    float d_01 = mix(d_0, d_1, t01);
    float d_12 = mix(d_01, d_2, t12);
    float d_23 = mix(d_12, d_3, t23);
    float d_30 = mix(d_23, d_0, t30);
    return d_30;
}

float march(vec3 o, vec3 r, inout Material material)
{
    float d = 0.0, t = NEAR;
    vec3 p = o;
    for (int i = 0; i < MARCHING_STEPS; i++)
    {
        p = o + r * t;
        d = sdf_world(p, material);
        if (d < NEAR || t > FAR) { break; }
        t += d;
    }
    return t;
}

mat3 lookat(vec3 o, vec3 t)
{
    vec3 f = normalize(t - o);
    vec3 r = cross(f, vec3(0.0, 1.0, 0.0));
    vec3 u = cross(r, f);
    return mat3(r, u, f);
}

vec3 normalat(vec3 p, inout Material tempmat)
{
    const vec2 e = vec2(0.002, 0.0);
    float d = sdf_world(p, tempmat);
    vec3 d2 = vec3(d) - vec3(
        sdf_world(p - e.xyy, tempmat),
        sdf_world(p - e.yxy, tempmat),
        sdf_world(p - e.yyx, tempmat)
    );
    return normalize(d2);
}

void main()
{
    vec2 uv = vs_pos.xy;
    
    vec3 o = vec3(0.0);
    float camera_rotation = u_time * 2.0;
    float camera_height = 7.0;
    o.x = cos(camera_rotation) * 10.0;
    o.y = camera_height;
    o.z = sin(camera_rotation) * 10.0;

    Material material;
    material.albedo = vec3(0.5, 0.5, 0.5);

    vec3 t = vec3(0.0, 0.0, 0.0);
    vec3 r = lookat(o, t) * normalize(vec3(uv, 1.0));
    float d = march(o, r, material);
    vec3 rgb = vec3(0.12 - uv.y * 0.06);
    if (d < FAR)
    {
        Material _tempmat;

        vec3 P = o + r * d;
        vec3 N = normalat(P, _tempmat);
        vec3 L = normalize((o + vec3(-2.0, 2.0, 0.0)) - P);

        float lambert = dot(N, L);
        lambert = max(lambert, 0.0);

        rgb = material.albedo * lambert;
    }

    fs_color = vec4(rgb, 1.0);
}
