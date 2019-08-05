#version 460

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer bind_0
{
    vec4 dat_0[];
};

uniform uvec2 u_wh;


float sphere(vec3 p, float r)
{
    return length(p) - r;
}


float world(vec3 p)
{
    float d_sphere = sphere(p, 2.0);

    return d_sphere;
}


float raymarch(vec3 o, vec3 r)
{
    float t;
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
    vec2 e = vec2(1.0 / float(max(u_wh.x, u_wh.y)), 0.0);
    return normalize(vec3(
        world(p + e.xyy) - world(p - e.xyy),
        world(p + e.yxy) - world(p - e.yxy),
        world(p + e.yyx) - world(p - e.yyx)
    ));
}


void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;
    uint i = xy.x + xy.y * u_wh.x;

    vec2 uv = vec2(xy) / vec2(u_wh);

    vec3 o = vec3(0.0, 0.0, -5.0);
    vec3 r = normalize(vec3(uv * 2.0 - 1.0, 1.01));

    vec3 rgb = vec3(uv, max(1.0 - uv.x - uv.y, 0.0));

    float t = raymarch(o, r);
    vec3 P = o + r * t;
    vec3 L = normalize(vec3(-2.0, 2.0, -2.0));
    vec3 N = normal_at(P);

    float lambert = dot(N, L);
    lambert = clamp(lambert, 0.0, 1.0);

    rgb.xyz = vec3(lambert);

    rgb = clamp(rgb, 0.0, 1.0);
    dat_0[i] = vec4(rgb, 1.0);
}
