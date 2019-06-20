
#version 460

#define saturate(x) min(max(x, 0.0), 1.0)

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer bind_0
{
    vec4 data_0[];
};

uniform uint u_width;
uniform uint u_height;


float sphere(vec3 p, float r)
{
    return length(p) - r;
}

float world(vec3 p)
{
    return sphere(p, 2.0);
}

float march(vec3 o, vec3 r)
{
    float t = 0.0;
    float d;
    vec3 p;

    for (int i = 0; i < 64; i++)
    {
        p = o + r * t;
        d = world(p);
        if (d < 0.02)
        {
            break;
        }
        t += d;
    }
    return t;
}

vec3 normal_at(vec3 p)
{
    vec2 e = vec2(0.002, 0.0);
    return normalize(vec3(
        world(p + e.xyy) - world(p - e.xyy),
        world(p + e.yxy) - world(p - e.yxy),
        world(p + e.yyx) - world(p - e.yyx)
    ));
}

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * 8;
    uint i = xy.x + xy.y * u_width;

    vec2 uv = vec2(vec2(xy) / vec2(u_width, u_height));
    vec2 cuv = uv * 2.0 - 1.0;

    vec3 o = vec3(0.0, 0.0, -5.0);
    vec3 r = normalize(vec3(cuv, 1.0));
    float t = march(o, r);

    vec3 light_pos = vec3(-5.0, 5.0, 10.0);
    vec3 rgb = vec3(uv, 0.2);
    if (t < 100.0)
    {
        vec3 P = o + r * t;
        vec3 N = normal_at(P);
        vec3 L = normalize(P - light_pos);

        float ndl = saturate(dot(N, L));

        rgb = vec3(ndl);
    }

    data_0[i] = vec4(rgb, 1.0);
}