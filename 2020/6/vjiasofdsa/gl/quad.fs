#version 460

#define PI 3.14159284
#define PI2 6.28318568
#define FAR 5000.0

in vec4 vs_pos;
out vec4 fs_color;

uniform float u_time;
uniform vec3 u_campos;
uniform vec2 u_resolution;
layout(location=0) uniform sampler2D u_tex;

struct Material
{
    vec3 color;
};

float hash11(float x)
{
    return fract(sin(x) * 43215.43215788);
}

float hash12(vec2 uv)
{
    return hash11(dot(uv, vec2(12.7878, 78.41325)));
}

float hash13(vec3 pos)
{
    return hash11(dot(pos, vec3(12.7878, 0.52314, 78.41325)));
}

float noise(vec2 uv)
{
    vec2 coord = floor(uv);
    float a = hash12(coord);
    float b = hash12(coord + vec2(1.0, 0.0));
    float c = hash12(coord + vec2(0.0, 1.0));
    float d = hash12(coord + vec2(1.0, 1.0));

    vec2 f = fract(uv);
    vec2 u = f * f * (3.0 - 2.0 * f);

    float ab = (b - a) * u.x + a;
    float ca = (c - a) * u.y * (1.0 - u.x);
    float db = (d - b) * u.x * u.y;
    return ab + ca + db;
}

float sdf_sphere(vec3 p, float rad) { return length(p) - rad; }

float sdf_plane(vec3 p, vec3 normal, float dist) { return dot(p, normal) - dist; }

float sdf_world(vec3 p, inout Material mat)
{
    float d_sphere = sdf_sphere(p, 3000.0);
    float d_terrain = sdf_plane(p, vec3(0.0, 1.0, 0.0), -5.0);

    mat.color = vec3(1.0);
    if (d_terrain < -d_sphere)
    {
        mat.color = vec3(0.0, 1.0, 0.0);
    }
    return min(-d_sphere, d_terrain);
}

float march(vec3 o, vec3 r, inout Material mat)
{
    vec3 p = o;
    float t = 0.0, d = 0.0;

    for (int i = 0; i < 32; i++)
    {
        p = o + r * t;
        d = sdf_world(p, mat);
        if (d < 0.01 || t > FAR) { break; }
        t += d;
    }
    return t;
}

mat3 lookat(vec3 o)
{
    const vec3 UP = vec3(0.0, 1.0, 0.0);
    vec3 f = normalize(o);
    vec3 r = cross(f, UP);
    vec3 u = cross(r, f);
    return mat3(r, u, f);
}

vec3 normal_at(vec3 p, inout Material mat)
{
    const vec2 e = vec2(0.002, 0.0);
    return normalize(sdf_world(p, mat) - vec3(
        sdf_world(p - e.xyy, mat),
        sdf_world(p - e.yxy, mat),
        sdf_world(p - e.yyx, mat)
    ));
}

void main()
{
    vec2 puv = vs_pos.xy;
    puv.x *= u_resolution.y / u_resolution.x;
    vec3 rgb = vec3(0.2, 0.3, 0.4);

    vec3 o = u_campos;
    vec3 r = lookat(o) * normalize(vec3(puv, 1.0));
    Material mat;
    float t = march(o, r, mat);
    if (t < FAR)
    {
        vec3 p = o + r * t;
        vec3 n = normalize(-p);

        vec2 uv = vec2(0.0);
        uv.x = atan(n.z, n.x) / PI2;
        uv.y = atan(n.y, length(n.xz));

        float noised = noise(uv * vec2(PI * 42.0, PI * 12.0));
        float horizontal_clip = smoothstep(1.0, 0.32, -uv.y);

        float x = horizontal_clip + uv.x;

        rgb = mat.color * x;
    }

    fs_color = vec4(rgb, 1.0);
}
