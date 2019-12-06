#version 460

layout(binding=15) buffer gpu_const
{
    float u_time;
};

struct Material
{
    vec3 color;
};

in vec2 vs_pos;
out vec4 fs_color;


float sdf_sphere(vec3 p, float radius)
{
    return length(p) - radius;
}

float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    vec3 d1 = max(d, 0.0);
    vec3 d2 = min(d, 0.0);
    return length(d1) + max(d2.x, max(d2.y, d2.z));
}

float op_union_round(float a, float b, float t)
{
    vec2 uu = max(vec2(t - a, t - b), 0.0);
    return max(t, min(a, b)) - length(uu);
}

float sdf(vec3 p, bool is_color, inout Material material)
{
    vec3 q = p;

    material.color = vec3(1.0, 0.0, 0.0);

    float jump = cos(u_time * 3.0) * 0.5 + 0.5;
    jump = pow(-jump, 5.0) * 7.0 + 3.0;
    q.y += jump;

    vec3 q_sph = q - vec3(-1.4, 0.0, 0.0);
    q_sph.x += cos(u_time * 7.0) * 0.5;
    float d_sph_0 = sdf_sphere(q_sph, 1.5);

    vec3 q_box = q - vec3(1.5, 0.0, 0.0);
    float c, s;
    c = cos(u_time * 4.0);
    s = sin(u_time * 4.0);
    q_box.xz = mat2(c, s, -s, c) * q_box.xz;
    float d_box_0 = sdf_box(q_box, vec3(1.4)) - 0.1;

    float blend = abs(jump - 3.0) * 0.3 + 0.2;
    float distance = op_union_round(d_sph_0, d_box_0, blend);

    const float freq = 40.0;
    const float disp = 0.01;
    distance += cos(p.x * freq) * cos(p.y * freq) * cos(p.z * freq) * disp;

    if (is_color)
    {
        vec3 color = d_box_0 < d_sph_0 ? vec3(0.9, 0.2, 0.2) : vec3(0.2, 0.2, 0.9);
        material.color = color;
    }

    return distance;
}

float march(vec3 o, vec3 r, inout Material material)
{
    vec3 p;
    float t = 0.5;
    float d;

    for (; t < 100.0;)
    {
        p = o + r * t;
        d = sdf(p, true, material);
        if (d < 0.05)
        {
            break;
        }
        t += d;
    }
    return t;
}

mat3 lookat(vec3 o, vec3 t)
{
    const vec3 UP = vec3(0.0, 1.0, 0.0);
    vec3 F = normalize(t - o);
    vec3 R = cross(F, UP);
    vec3 U = cross(R, F);

    return mat3(R, U, F);
}

vec3 normalat(vec3 p)
{
    const vec2 E = vec2(0.02, 0.0);
    Material _m;
    return normalize(vec3(
        sdf(p + E.xyy, false, _m) - sdf(p - E.xyy, false, _m),
        sdf(p + E.yxy, false, _m) - sdf(p - E.yxy, false, _m),
        sdf(p + E.yyx, false, _m) - sdf(p - E.yyx, false, _m)
    ));
}

void main()
{
    vec2 uv = vs_pos * 0.5 + 0.5;
    vec3 RGB = vec3(0.12 - uv.y * 0.08);

    vec3 org = vec3(-3.5, 1.5, -6.5);
    vec3 focus = vec3(0.0, 0.0, 0.0);

    vec2 pos = vs_pos;
    vec3 ray = lookat(org, focus) * normalize(vec3(pos, 1.0));

    vec3 light_pos = vec3(-40.0, 40.0, -40.0);

    Material material;
    float T = march(org, ray, material);
    if (T < 100.0)
    {
        vec3 P = org + ray * T;
        vec3 N = normalat(P);
        vec3 L = normalize(light_pos - P);
        vec3 H = normalize(L - ray);

        float blinn = dot(N, H);
        blinn = max(blinn, 0.0);
        blinn = pow(blinn + 0.005, 32.0);
        blinn = min(blinn, 1.0);

        float fresnel = 1.0 - dot(N, -ray);
        fresnel = max(fresnel, 0.0);
        fresnel = pow(fresnel, 3.0);
        fresnel *= 0.25;

        float lambert = dot(N, L);
        lambert = max(lambert, 0.0);

        vec3 specular = blinn * vec3(0.99, 0.99, 0.88) + fresnel * vec3(0.75, 0.66, 0.5);
        vec3 diffuse = (1.0 - specular) * lambert * material.color;
        vec3 ambient = (1.0 - (diffuse + specular)) * vec3(0.12);

        vec3 light = specular + diffuse + ambient;

        RGB = light;
    }

    fs_color = vec4(RGB, 1.0);
}
