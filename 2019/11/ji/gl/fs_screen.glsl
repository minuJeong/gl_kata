#version 460

in vec3 vs_pos;

out vec4 fs_color;

uniform float u_time;


float sdf_sphere(vec3 p, float radius)
{
    return length(p) - radius;
}

float sdf_box(vec3 p, vec3 b)
{
    vec3 bb = abs(p) - b;
    return max(max(bb.x, bb.y), bb.z);
}

float world(vec3 p)
{
    float distance_sphere = sdf_sphere(p - vec3(-1.0, cos(u_time * 3.0) * 0.6, 0.0), 2.0);
    float distance_box = sdf_box(p - vec3(+1.0, 0.0, 0.0), vec3(2.0));

    float distance = min(distance_sphere, distance_box);
    return distance;
}

float raymarch(vec3 o, vec3 r)
{
    vec3 p;
    float t;
    float d;

    for (int i = 0; i < 48; i++)
    {
        p = o + r * t;
        d = world(p);
        if (d < 0.02 || t > 100.0)
        {
            break;
        }
        t += d;
    }
    return t;
}

mat3 lookat(vec3 o, vec3 to)
{
    vec3 up = vec3(0.0, 1.0, 0.0);
    vec3 front = normalize(to - o);
    vec3 right = cross(front, up);
    vec3 local_up = cross(right, front);
    return mat3(right, local_up, front);
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
    const float CAM_DIST = 6.0;
    vec3 camera_position = vec3(
        cos(u_time * 2.0) * CAM_DIST,
        4.0,
        sin(u_time * 2.0) * CAM_DIST);
    vec3 camera_ray = lookat(camera_position, vec3(0.0)) * normalize(vec3(vs_pos.xy, 1.0));

    vec3 RGB = vec3(0.1);
    float t = raymarch(camera_position, camera_ray);
    if (t < 100.0)
    {
        vec3 L = normalize(vec3(-4.0, 4.0, -3.0));

        vec3 P = camera_position + camera_ray * t;
        vec3 N = normal_at(P);

        float lambert = max(dot(N, L), 0.0);

        float ambient = (1.0 - lambert) * 0.2;

        float lighting = lambert + ambient;

        RGB = vec3(lighting);
    }

    fs_color = vec4(RGB, 1.0);
}
