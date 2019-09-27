#version 460
#include ./hg_sdf.glsl

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer color
{
    vec4 out_col[];
};

uniform vec2 u_resolution;


float world(vec3 p)
{
    float dist_sphere = fSphere(p - vec3(-1.0, 0.0, 0.0), 2.0);
    float dist_box = fBox(p - vec3(2.0, 0.0, 0.0), vec3(1.0));
    return fOpUnionRound(dist_sphere, dist_box, 0.5);
}

float raymarch(vec3 o, vec3 r)
{
    float t;
    float d;
    vec3 p;

    for (int i = 0; i < 48; i++)
    {
        p = o + r * t;
        d = world(p);
        if (d < 0.02 || t > 50.0)
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
    return normalize(vec3(
        world(p + e.xyy) - world(p - e.xyy),
        world(p + e.yxy) - world(p - e.yxy),
        world(p + e.yyx) - world(p - e.yyx)
    ));
}

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;
    vec2 uv = vec2(xy) / u_resolution;

    vec2 cuv = uv * 2.0 - 1.0;
    vec3 o = vec3(0.0, 0.0, -5.0);
    vec3 r = normalize(vec3(cuv, 1.0));
    float distance = raymarch(o, r);
    vec3 p = o + r * distance;
    vec3 n = normal_at(p);

    vec3 lambert_color = vec3(dot(n, normalize(vec3(-2.0, -2.0, -1.0))));
    lambert_color = min(max(lambert_color, 0.0), 1.0) * vec3(1.0, 0.0, 0.0);

    vec3 floor_light = vec3(0.0, 1.0, 0.0);
    float floor_color = min(max(dot(n, floor_light), 0.0), 1.0);
    lambert_color += floor_color * vec3(0.0, 0.0, 1.0);

    vec3 RGB = distance > 10.0 ? vec3(0.0) : lambert_color;

    uint i = uint(xy.x + xy.y * u_resolution.y);
    out_col[i] = vec4(RGB, 1.0);
}
