#version 460

#define FAR 100.0
#define NEAR 0.02
#define UP vec3(0.0, 1.0, 0.0)
#define Z3 vec3(0.0, 0.0, 0.0)

in vec4 vs_pos;
out vec4 vs_color;

uniform vec2 u_resolution;
uniform float u_time;

float vmax(vec3 v) { return max(v.x, max(v.y, v.z)); }

mat3 lookat(vec3 a, vec3 b)
{
    vec3 z = normalize(b - a);
    vec3 x = normalize(cross(z, UP));
    vec3 y = normalize(cross(x, z));
    return mat3(x, y, z);
}

float sdf_sphere(vec3 p, float radius) { return length(p) - radius; }

float sdf_box(vec3 p, vec3 b)
{
    vec3 b0 = abs(p) - b;
    vec3 b1 = max(b0, Z3);
    vec3 b2 = min(b0, Z3);
    return length(b1) + vmax(b2);
}
float sdf_box(vec3 p, float b) { return sdf_box(p, vec3(b, b, b)); }

float world(vec3 p)
{
    // return sdf_sphere(p, 2.0);
    return sdf_box(p, 2.0);
}

float march(vec3 o, vec3 r)
{
    vec3 p;
    float d, t;
    for (int i = 0; i < 48; i++)
    {
        p = o + r * t;
        d = world(p);
        if (d < NEAR || t > FAR) { break; }
        t += d;
    }
    return t;
}

vec3 normal_at(vec3 pos)
{
    vec2 e = vec2(0.002, 0.0);
    return normalize(world(pos) - vec3(
        world(pos - e.xyy),
        world(pos - e.yxy),
        world(pos - e.yyx)
    ));
}

void main()
{
    vec2 uv = vs_pos.xy;
    uv.x /= u_resolution.y / u_resolution.x;

    float y = 0.09 - uv.y * 0.08;
    vec3 rgb = vec3(y, y, y);

    vec3 camera_pos = vec3(0.0, 4.0, 0.0);
    camera_pos.x = cos(u_time * 1.65) * 6.0;
    camera_pos.z = sin(u_time * 1.65) * 6.0;

    vec3 ray = lookat(camera_pos, Z3) * normalize(vec3(uv, 1.0));
    float travel = march(camera_pos, ray);
    if (travel < FAR)
    {
        vec3 pos = camera_pos + ray * travel;
        vec3 normal = normal_at(pos);
        vec3 light = normalize(vec3(-5.0, 10.0, 10.0) - pos);

        float lambert = dot(normal, light);
        lambert = max(lambert, 0.2);

        rgb = vec3(lambert, lambert, lambert);
    }
    vs_color = vec4(rgb, 1.0);
}
