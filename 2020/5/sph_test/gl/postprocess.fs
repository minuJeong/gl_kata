#version 460

in vec4 vs_pos;
out vec4 fs_color;

layout(location=0) uniform sampler2D gb_color;

struct Particle
{
    vec4 position;
    vec4 velocity;
    vec4 texcoord0;
};

layout(binding=0) buffer particles_buffer
{
    Particle particles[];
};

struct Grid
{
    vec4 velocity;
    float density;
};

layout(binding=1) buffer grid_buffer
{
    Grid grids[];
};

uniform vec3 u_camera_pos;
uniform vec3 u_camera_focus;
uniform vec2 u_resolution;

float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(b.x, max(b.y, b.z)), 0.0);
}

float sdf_world(vec3 p)
{
    float b = sdf_box(p, vec3(1.0));
    return b;
}

float march(vec3 o, vec3 r)
{
    vec3 p = o;
    float t = 0.0, d = 0.0;
    for (int i = 0; i < 64; i++)
    {
        p = o + r * t;
        d = sdf_world(p);
        if (d < 0.001 || t > 100.0) { break; }
        t += d;
    }
    return t;
}

mat3 lookat(vec3 o, vec3 f)
{
    vec3 ff = normalize(f - o);
    vec3 r = cross(ff, vec3(0.0, 1.0, 0.0));
    vec3 u = cross(r, ff);
    return mat3(r, u, ff);
}

float gb_at(vec2 uv)
{
    vec4 texcol = texture(gb_color, uv);
    float x = length(texcol.xyz);
    return x;
}

void main()
{
    vec2 uv = vs_pos.xy * 0.5 + 0.5;

    vec3 rgb = vec3(0.0);
    float alpha = 0.0;

    const vec2 e = vec2(0.002, 0.0);
    float x = gb_at(uv);
    float dx = x - gb_at(uv - e.xy);
    float dy = x - gb_at(uv - e.yx);
    vec3 N = normalize(vec3(dx, dy, 1.0));

    x = smoothstep(0.02, 0.12, x);
    rgb = mix(vec3(0.2, 0.23, 0.32), vec3(0.34, 0.7, 0.8), x);
    rgb *= max(dot(N, normalize(vec3(3, 4, 5))), 0.0);

    uv = uv * 2.0 - 1.0;
    uv.x *= u_resolution.x / u_resolution.y;

    vec3 o = u_camera_pos;
    vec3 r = lookat(o, u_camera_focus) * normalize(vec3(uv, 1.0));
    r = normalize(r);

    float t = march(o, r);
    if (t < 100.0)
    {
        rgb.x = 1.0;
    }

    fs_color = vec4(rgb, 1.0);
}
