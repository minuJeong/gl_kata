#version 460

#define NEAR 0.0002
#define FAR 100.0

layout(binding=2) buffer constants
{
    float u_aspect;
    float u_time;
};

in vec4 vs_pos;
out vec4 fs_colour;

const vec3 UP = vec3(0.0, 1.0, 0.0);


float sdf_sphere(vec3 p, float radius)
{
    return length(p) - radius;
}

float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    vec3 d0 = max(d, vec3(0.0));
    vec3 d1 = min(d, vec3(0.0));
    return length(d0) + max(d1.x, max(d1.y, d1.z));
}
float sdf_box(vec3 p, float b) { return sdf_box(p, vec3(b)); }

float op_union_round(float a, float b, float r)
{
    vec2 uv = max(vec2(r - a, r - b), vec2(0.0, 0.0));
    return max(r, min(a, b)) - length(uv);
}

float sdf_world(vec3 p)
{
    float d_sphere = sdf_sphere(p - vec3(1.0, 0.0, 0.0), 1.0);
    float d_box = sdf_box(p - vec3(-1.0, 0.0, 0.0), 0.9) - 0.1;
    return op_union_round(d_sphere, d_box, 0.5);
}

float marching(vec3 o, vec3 r)
{
    vec3 p;
    float t, d;
    for (float i = 0.0; i < 256.0; i+=1.0)
    {
        p = o + r * t;
        d = sdf_world(p);
        if (d < NEAR || t > FAR) { break; }
        t += d;
    }
    return t;
}

mat3 lookzero(vec3 pos)
{
    vec3 f = normalize(-pos);
    vec3 r = cross(f, UP);
    vec3 u = cross(r, f);
    return mat3(r, u, f);
}

vec3 normalat(vec3 p)
{
    const vec2 e = vec2(NEAR, 0.0);
    return normalize(sdf_world(p) - vec3(
        sdf_world(p - e.xyy),
        sdf_world(p - e.yxy),
        sdf_world(p - e.yyx)
    ));
}

void main()
{
    vec3 RGB;
    float alpha = 1.0;

    vec2 uv = vs_pos.xy;
    RGB = vec3(0.3 - uv.y * 0.3);

    alpha = pow(1.0 - length(uv), 0.6);

    float rot_speed = 0.4;

    vec3 origin = vec3(0.0, 2.2, -5.0);
    origin.x = cos(u_time * rot_speed) * 10.0;
    origin.z = sin(u_time * rot_speed) * 10.0;

    vec3 light_pos = vec3(-10.0, 10.0, -10.0);

    vec3 ray = lookzero(origin) * normalize(vec3(uv, 2.5));
    float t = marching(origin, ray);
    if (t < FAR)
    {
        vec3 P = origin + ray * t;
        vec3 N = normalat(P);
        vec3 L = normalize(light_pos - P);
        vec3 V = -ray;
        vec3 H = normalize(L + V);

        float blinn = dot(N, H);
        blinn = max(blinn, 0.0);
        blinn = pow(blinn, 32.0) * 0.25;

        float fresnel = 1.0 - dot(N, H);
        fresnel = max(fresnel, 0.0);
        fresnel = pow(fresnel, 5.0) * 0.1;

        float lambert = dot(N, L);
        lambert = max(lambert, 0.0);

        float light_atten = blinn + fresnel + lambert;

        RGB = vec3(light_atten);
    }

    fs_colour = vec4(RGB * alpha, alpha);
}
