#version 460

#define NEAR 0.002
#define FAR 100.0

in vec2 vs_pos;
out vec4 fs_color;

layout(binding=1) buffer b_screen_draw
{
    vec4 b_draw_rgb[];
};

uniform float u_time;
uniform vec3 u_slider_pos;
uniform uvec2 u_res;
uniform bool u_is_draw;

struct Material
{
    vec3 P;
    float t;
    vec3 base_color;
};

const vec3 UP = vec3(0.0, 1.0, 0.0);


float sdf_sphere(vec3 p, float rad)
{
    return length(p) - rad;
}

float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    vec3 d0 = max(d, 0.0);
    vec3 d1 = min(d, 0.0);
    return length(d0) + max(d1.x, max(d1.y, d1.z));
}

float sdf_plane(vec3 p, vec3 n, float d)
{
    return dot(p, n) + d;
}

float op_union_round(float a, float b, float t)
{
    vec2 u = max(vec2(t - a, t - b), 0.0);
    return max(t, min (a, b)) - length(u);
}

float sdf_world(vec3 p, inout Material material)
{
    float floor_height;
    uvec2 xy = uvec2(p.xz * 24.0 + u_res.x * 0.5);
    if (xy.x > 0 && xy.x < u_res.x - 1 &&
        xy.y > 0 && xy.y < u_res.y - 1)
    {
        uint i = xy.x + xy.y * u_res.x;
        vec3 buf_value = b_draw_rgb[i].xyz;
        material.base_color = buf_value;
        floor_height = buf_value.x * 2.0 - 2.0;
    }
    else
    {
        material.base_color = vec3(0.2, 0.2, 0.4);
    }

    float distance = sdf_plane(p - vec3(0.0, -12.0 + u_slider_pos.z * 24.0, 0.0), UP, 0.0);

    {
        vec3 q = p;
        q -= vec3(-1.5, 0.0, 0.0);
        float d = sdf_box(q, vec3(1.3)) - 0.2;

        if (d < distance)
        {
            material.base_color = vec3(0.0, 1.0, 0.0);
        }
        distance = min(distance, d);
    }

    {
        vec3 q = p;
        q -= vec3(1.5, 0.0, 0.0);
        float d = sdf_sphere(q, 1.5);

        if (d < 0.5)
        {
            material.base_color = vec3(1.0, 0.0, 0.0);
        }
        distance = op_union_round(distance, d, 0.5);
    }

    return distance;
}

void march(vec3 o, vec3 r, inout Material material)
{
    float d, t;
    vec3 p;
    for (int i = 0; i < 64; i++)
    {
        p = o + r * t;
        material.P = p;
        d = sdf_world(p, material);
        if (d < NEAR || t > FAR) {break;}
        t += d;
    }
    material.t = t;
}

mat3 lookzero(vec3 o)
{
    vec3 lsforw = normalize(-o);
    vec3 lsright = cross(lsforw, UP);
    vec3 lsup = cross(lsright, lsforw);
    return mat3(lsright, lsup, lsforw);
}

vec3 normalat(vec3 p)
{
    Material _m;

    const vec2 e = vec2(NEAR, 0.0);
    return normalize(sdf_world(p, _m) - vec3(
        sdf_world(p - e.xyy, _m),
        sdf_world(p - e.yxy, _m),
        sdf_world(p - e.yyx, _m)
    ));
}

void main()
{
    const vec3 ambient_color = vec3(0.06, 0.01, 0.12);

    vec2 uv = vs_pos.xy;

    vec3 org = vec3(0.0);
    org.y = 4.0 * u_slider_pos.y * 24.0;
    org.x = 2.0 + u_slider_pos.x * 24.0;
    org.z = 8.0 + u_slider_pos.x * 24.0;

    vec3 ray = lookzero(org) * normalize(vec3(uv, 1.0));

    Material material;
    material.base_color = vec3(0.2, 0.2, 0.7);
    march(org, ray, material);

    vec3 RGB = vec3(-uv.y * 0.03 + 0.05);
    if (material.t < FAR)
    {
        vec3 light_pos = vec3(0.0);
        light_pos.y = 12.0;
        light_pos.x = sin(u_time * 4.0) * 8.0;
        light_pos.z = cos(u_time * 4.0) * 8.0;

        vec3 P = material.P;
        vec3 N = normalat(P);
        vec3 L = normalize(light_pos - P);

        float diffuse = dot(N, L);
        diffuse = max(diffuse, 0.0);
        vec3 diffuse_light = diffuse * material.base_color;
        float ambient = 1.0;
        vec3 ambient_light = ambient * ambient_color;

        vec3 light = diffuse_light + ambient_light;

        RGB = light;
    }

    if (u_is_draw)
    {
        uv.y = - uv.y;
        uvec2 xy = uvec2(uv * 256 + 256);
        uint i = xy.x + xy.y * u_res.x;
        vec3 buf_value = b_draw_rgb[i].xyz;
        RGB.x = buf_value.x;
    }

    RGB = clamp(RGB, 0.0, 1.0);
    fs_color = vec4(RGB, 1.0);
}
