#version 460

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer bind_0
{
    vec4 data_0[];
};

uniform uint u_width;
uniform uint u_height;
uniform float u_time;


float sphere(vec3 p, float r)
{
    return length(p) - r;
}

float world(vec3 p)
{
    return sphere(p, 3.0);
}

float raymarch(vec3 o, vec3 r)
{
    vec3 p;
    float t;
    float d;

    for (int i = 0; i < 64; i++)
    {
        p = o + r * t;
        d = world(p);
        if (d < 0.002)
        {
            break;
        }
        t += d;
    }
    return t;
}

vec3 normal_at(vec3 p)
{
    vec2 e = vec2(0.0002, 0.0);
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

    uvec2 wh = uvec2(u_width, u_height);
    vec2 uv = vec2(vec2(xy) / vec2(wh));
    vec2 cuv = uv * 2.0 - 1.0;

    vec3 rgb = vec3(uv, 0.5);
    vec3 light_pos = vec3(-2.0, 10.0, 5.0);

    vec3 o = vec3(0.0, 0.0, -5.0);
    vec3 r = normalize(vec3(cuv, 1.01));

    float t = raymarch(o, r);

    if (t < 4.0)
    {
        vec3 P = o + r * t;
        vec3 N = normal_at(P);
        vec3 L = normalize(P - light_pos);
        vec3 V = normalize(P - o);
        vec3 H = normalize(L + V);

        // float phong = clamp(0.0, 1.0, dot(N, L));
        // phong += max(dot(N, H), 0.0);
        rgb = abs(N);
    }

    rgb = min(max(rgb, 0.0), 1.0);
    data_0[i] = vec4(rgb, 1.0);
}
