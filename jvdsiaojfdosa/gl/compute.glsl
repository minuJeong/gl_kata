#version 460

#define saturate(x) min(max(x, 0.0), 1.0)

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer buffer_0
{
    vec4 buf_dat[];
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
    return sphere(p, 2.0);
}

float raymarch(vec3 o, vec3 r)
{
    float t = 0.0;
    float d = 0.0;
    vec3 p;
    for (int i = 64; i >= 0; i--)
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
    vec2 e = vec2(0.02, 0.0);
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
    vec3 rgb = vec3(0.0);
    vec3 sun = vec3(-2.0, 10.0, 5.0);

    vec2 wh = vec2(u_width, u_height);
    vec2 uv = vec2(xy / wh);

    vec3 o = vec3(0.0, 0.0, -5.0);
    vec3 r = normalize(vec3(uv * 2.0 - 1.0, 1.0));

    float t = raymarch(o, r);
    vec3 P = o + r * t;
    vec3 N = normal_at(P);
    vec3 L = normalize(P - sun);
    vec3 V = -r;
    vec3 H = normalize(V + L);

    float diffuse = saturate(dot(N, L));
    float specular = saturate(pow(dot(N, H), 5.0));
    float lit = diffuse + specular;
    lit /= exp(t * 0.2);

    rgb = vec3(lit, lit, lit);

    rgb = saturate(rgb);
    buf_dat[i] = vec4(rgb, 1.0);
}
