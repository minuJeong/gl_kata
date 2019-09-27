#version 460

#include ./gl/hg_sdf.glsl

#define NEAR 0.002
#define FAR 10.0

in vec2 vs_pos;
in vec2 vs_uv;

out vec4 fs_color;

uniform float u_time;


float world(vec3 p, out vec3 color)
{
    float distance = FAR;

    float distance_icosa = fIcosahedron(p, 1.5, 48.0);
    {
        if (distance_icosa < distance)
        {
            color = vec3(0.0, 1.0, 0.0);
        }
    }

    float distance_capsule;
    {
        float c, s;
        c = cos(u_time * 2.5);
        s = cos(u_time * 2.5);

        vec3 j1 = vec3(2.1, 1.0, 0.0);
        j1.xz = mat2(c, -s, s, c) * j1.xz;
        distance_capsule = fCapsule(p - j1, 0.75, 1.25);

        if (distance_capsule < distance_icosa)
        {
            color = mix(vec3(1.0, 0.0, 0.0), color,
                distance_capsule / distance_icosa
            );
        }
    }

    float distance_objects = 
        fOpUnionRound(distance_icosa, distance_capsule, 0.5);

    float distance_plane = fPlane(p, vec3(0.0, 1.0, 0.0), 2.0);
    {
        if (distance_plane < distance_objects)
        {
            color = vec3(1.0);
        }
    }
    distance = min(distance_objects, distance_plane);

    return distance;
}

float raymarch(vec3 o, vec3 r, out vec3 color)
{
    vec3 p;
    float d;
    float t;

    for (int i = 0; i < 64; i++)
    {
        p = o + r * t;
        d = world(p, color);
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
    vec3 up = vec3(0.0, 1.0, 0.0);
    vec3 forward = normalize(t - o);
    vec3 local_up = normalize(cross(forward, up));
    vec3 local_right = normalize(cross(local_up, forward));

    return mat3(local_up, local_right, forward);
}

vec3 normal_at(vec3 p)
{
    const vec2 e = vec2(0.002, 0.0);
    vec3 _ = vec3(0.0);
    return normalize(vec3(
        world(p + e.xyy, _) - world(p - e.xyy, _),
        world(p + e.yxy, _) - world(p - e.yxy, _),
        world(p + e.yyx, _) - world(p - e.yyx, _)
    ));
}

vec3 enlighten(vec3 V, vec3 L, vec3 P, float distance, vec3 color)
{
    vec3 rgb = vec3(0.5);

    L = normalize(L - P);

    vec3 H = (L + V) * 0.5;

    vec3 N = normal_at(P);

    float main_light = saturate(dot(N, L));
    float floor_reflection = saturate(dot(N, vec3(0.0, -1.0, 0.0)));
    float ambient = 0.1;

    float specular = pow(saturate(dot(N, H)), 32.0);
    specular = smoothstep(0.8 , 1.0, specular);

    float light = main_light + floor_reflection;
    rgb = color * max(light, ambient) + specular * vec3(0.8, 0.6, 0.7 );

    rgb = mix(rgb, vec3(0.05), clamp(distance / FAR, 0.0, 1.0));
    rgb = saturate(rgb);

    return rgb;
}

void main()
{
    #define DISTANCE 4.0
    #define ROTATION_SPEED 0.5

    vec3 o = vec3(
        sin(u_time * ROTATION_SPEED) * DISTANCE,
        4.0,
        cos(u_time * ROTATION_SPEED) * DISTANCE);
    vec3 r = lookat(o, vec3(0.0)) * normalize(vec3(vs_pos, 1.0));

    vec3 color;
    float t = raymarch(o, r, color);
    vec3 P = o + r * t;
    vec3 V = -r;
    vec3 L = o;
    vec3 rgb = enlighten(V, L, P, t, color);

    fs_color = vec4(rgb, 1.0);
}
