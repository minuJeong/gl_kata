#version 460

in vec2 vs_pos;
out vec4 fs_color;

uniform ivec3 u_volume_res;
uniform float u_time = 0.0;

layout(binding=14) buffer truchet_volume_buffer
{
    vec4 volume[];
};

float sdf_sphere(vec3 p, float radius)
{
    return length(p) - radius;
}

float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    vec3 d0 = max(d, 0.0);
    vec3 d1 = min(d, 0.0);
    return length(d0) + max(d1.x, max(d1.y, d1.z));
}

float sdf_world(vec3 p)
{
    float d_box = sdf_box(p - vec3(0.0), vec3(0.88)) - 0.12;
    return d_box;
}

float raymarch(vec3 o, vec3 r)
{
    vec3 p;
    float d, t;
    for (int i = 0; i < 32; i++)
    {
        p = o + r * t;
        d = sdf_world(p);
        if (d < 0.002 || t > 100.0) { break; }
        t += d;
    }
    return t;
}

vec3 stepinside(vec3 o, vec3 r)
{
    const float STEP = 128.0;
    const float STEP_MOVE = 0.01;
    const float SCALE = 64.0;

    vec3 p;
    float t;
    vec3 color_accumulate;
    ivec3 R = u_volume_res;
    for (int i = 0; i < STEP; i++)
    {
        p = o + r * t;
        if (sdf_world(p) < 0.0)
        {
            ivec3 xyz = ivec3(floor(p * SCALE + SCALE));
            uint i = xyz.x + xyz.y * R.x + xyz.z * R.x * R.y;
            vec4 col = volume[i];
            color_accumulate += col.xyz;

            if (dot(color_accumulate, vec3(0.98, 0.01, 0.07)) > 1.0)
            {
                break;
            }
        }

        t += STEP_MOVE;
    }

    return color_accumulate;
}

mat3 lookatzero(vec3 org)
{
    const vec3 UP = vec3(0.0, 1.0, 0.0);
    vec3 forward = normalize(vec3(0.0) - org);
    vec3 right = cross(forward, UP);
    vec3 localup = cross(right, forward);
    return mat3(right, localup, forward);
}

vec3 normalat(vec3 p)
{
    const vec2 eps = vec2(0.002, 0.0);
    return normalize(vec3(
        sdf_world(p + eps.xyy) - sdf_world(p - eps.xyy),
        sdf_world(p + eps.yxy) - sdf_world(p - eps.yxy),
        sdf_world(p + eps.yyx) - sdf_world(p - eps.yyx)
    ));
}

void main()
{
    vec2 uv = vs_pos.xy;

    vec3 org;
    org.y = 1.5;
    org.x = cos(u_time * 0.25) * 2.4;
    org.z = sin(u_time * 0.25) * 2.4;
    vec3 ray = lookatzero(org) * normalize(vec3(uv, 1.0));

    float t = raymarch(org, ray);
    vec3 RGB;
    if (t < 100.0)
    {
        vec3 P = org + ray * t;
        vec3 N = normalat(P);
        vec3 L = normalize(vec3(2.0, 12.0, 5.0));

        vec3 volume_color = stepinside(P, ray);
        float diffuse = dot(N, L) * 0.5 + 0.5;

        RGB = volume_color * diffuse;
    }

    RGB = clamp(RGB, 0.0, 1.0);
    fs_color = vec4(RGB, 1.0);
}
