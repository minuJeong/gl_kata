#version 460

#define VOXEL_SIZE 2
#define VOXEL_RESOLUTION 4

in vec4 vs_pos;
out vec4 fs_colour;

struct Voxel
{
    float value;
};

layout(binding=0) buffer voxelbuffer
{
    Voxel voxel[];
};

uniform float u_time;
uniform vec2 u_resolution;
uniform vec2 u_cursor;
uniform int u_action;

float sdf_sphere(vec3 p, float radius) { return length(p) - radius; }
float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    return length(max(d, 0.0)) + min(0.0, max(d.x, max(d.y, d.z)));
}

float sdf_world(vec3 p)
{
    return sdf_box(p, vec3(2.0));
}

float march(vec3 o, vec3 r)
{
    vec3 p;
    float d = 0.0, t = 0.0;
    for (int i = 0; i < 64; i++)
    {
        p = o + r * t;
        d = sdf_world(p);
        if (d < 0.001 || t > 100.0) { break; }
        t += d;
    }
    return t;
}

mat3 look_zero(vec3 p)
{
    vec3 f = normalize(-p);
    vec3 r = cross(f, vec3(0.0, 1.0, 0.0));
    vec3 u = cross(r, f);
    return mat3(r, u, f);
}

vec3 normal_at(vec3 p)
{
    const vec2 e = vec2(0.002, 0.0);
    return normalize(sdf_world(p) - vec3(
        sdf_world(p - e.xyy),
        sdf_world(p - e.yxy),
        sdf_world(p - e.yyx)
    ));
}

void main()
{
    vec2 cursor = u_cursor / u_resolution;
    cursor = cursor * 2.0 - 1.0;

    vec2 uv = vs_pos.xy;
    vec3 rgb = vec3(0.12 - vs_pos.y * 0.06);
    vec3 o = vec3(0.0, 2.0, -5.0);
    o.x = cos(u_time) * 5.0;
    o.z = sin(u_time) * 5.0;
    vec3 r = look_zero(o) * normalize(vec3(uv, 1.0));
    float t = march(o, r);
    const vec3 light = normalize(vec3(-10.0f, 10.0f, -10.0f));

    if (t < 100.0)
    {
        rgb = vec3(0.0, 0.0, 0.0);
        vec3 p = o + r * t;
        vec3 n = normal_at(p);
        float lambert = dot(n, light);

        for (int i = 0; i < 32; i++)
        {
            p += r * (i * 0.02);
            vec3 uvw = floor((p * VOXEL_SIZE) / VOXEL_RESOLUTION);
            int voxel_index = int(uvw.x + uvw.y * VOXEL_RESOLUTION + uvw.z * VOXEL_RESOLUTION * VOXEL_RESOLUTION);
            float voxel_value = voxel[voxel_index].value;
            rgb += vec3(voxel_value) / (32.0 * 8.0);
        }
    }

    fs_colour = vec4(rgb, 1.0);
}
