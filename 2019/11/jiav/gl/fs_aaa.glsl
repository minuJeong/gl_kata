#version 460

#define NEAR 0.002
#define FAR 100.0

in vec2 vs_pos;

out vec4 fs_color;

uniform float u_time;


float sdf_sphere(vec3 p, float radius)
{
    return length(p) - radius;
}

float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    return max(d.x, max(d.y, d.z));
}

float sdf_plane(vec3 p, vec3 n, float d)
{
    return dot(p, n) - d;
}

float sdf_line(vec3 p, vec3 a, vec3 b)
{
    vec3 ba = b - a;
    float baba = dot(ba, ba);
    float t = min(max(dot(p - a, ba) / baba, 0.0), 1.0);
    return length(ba * t + a - p);
}

float op_union_round(float a, float b, float t)
{
    vec2 u = max(vec2(t - a, t - b), vec2(0.0));
    return max(min(a, b), t) - length(u);
}

float sdf(vec3 p)
{
    float distance;
    float d_sphere = sdf_sphere(p - vec3(-0.5, 0.0, 0.0), 0.5);
    float d_box = sdf_box(p - vec3(0.5, 0.0, 0.0), vec3(0.4));

    distance = min(d_sphere, d_box);

    float d_capsule = sdf_line(p, vec3(-1.0, 0.0, 0.0), vec3(+0.5, 0.5, 0.0)) - 0.2;
    distance = op_union_round(d_capsule, distance, 0.1);

    return distance;
}

float raymarch(vec3 o, vec3 r)
{
    vec3 p;
    float t;
    float d;

    for (int i = 0; i < 256; i++)
    {
        p = o + r * t;
        d = sdf(p);
        if (d < NEAR || t > FAR)
        {
            break;
        }
        t += d;
    }

    return t;
}

mat3 lookat(vec3 o, vec3 t)
{
    vec3 ws_up = vec3(0.0, 1.0, 0.0);
    vec3 forward = normalize(t - o);
    vec3 right = cross(forward,  ws_up);
    vec3 ls_up = cross(right, forward);
    return mat3(right, ls_up, forward);
}

vec3 normal_at(vec3 p)
{
    const vec2 e = vec2(NEAR, 0.0);
    return normalize(vec3(
        sdf(p + e.xyy) - sdf(p - e.xyy),
        sdf(p + e.yxy) - sdf(p - e.yxy),
        sdf(p + e.yyx) - sdf(p - e.yyx)
    ));
}

float shadow_at(vec3 o, vec3 r)
{
    float t = 0.1;
    for (int i = 0; i < 48; i++)
    {
        float d = sdf(o + r * t);
        if (d < NEAR)
        {
            return 0.0;
        }
        t += d;
    }
    return 1.0;
}

void main()
{
    vec3 camera = vec3(-4.0, 1.0, -7.0);

    float cam_dist = 1.8;
    camera.x = cos(u_time) * cam_dist;
    camera.z = sin(u_time) * cam_dist;

    vec3 ray = lookat(camera, vec3(0.0, 0.5, 0.0)) * normalize(vec3(vs_pos, 1.0));

    float travel = raymarch(camera, ray);
    vec3 RGB = vec3(0.1 - vs_pos.y * 0.05);
    if (travel < FAR)
    {
        vec3 P = camera + ray * travel;
        vec3 N = normal_at(P);
        vec3 L = normalize(vec3(-4.0, 4.0, -4.0));
        vec3 H = normalize(L - ray);

        float blinn = max(dot(N, H), 0.0);
        blinn = pow(blinn, 1024.0);
        blinn *= 2.0;

        float fresnel = 1.0 - dot(N, -ray);
        fresnel = pow(max(fresnel, 0.0), 12.0);
        fresnel *= 3.0;

        float specular = blinn + fresnel;
        specular = min(specular, 1.0);

        float lambert = max((1.0 - specular) * dot(N, L), 0.0);
        lambert *= 0.5;

        float ambient = (1.0 - lambert) * 0.2;

        float light = blinn + lambert + ambient;
        light = min(max(light, 0.0), 1.0);

        RGB = light.xxx;
    }

    fs_color = vec4(RGB, 1.0);
}
