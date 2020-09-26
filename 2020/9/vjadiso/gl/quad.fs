#version 460

in vec4 vs_pos;
out vec4 fs_color;

uniform float u_time;
uniform vec2 u_resolution;

highp float hash(vec2 coord)
{
    highp float x = dot(coord, vec2(12.3412, 45.43125));
    return fract(cos(x) * 41312.51324);
}

// https://iquilezles.org/www/articles/smin/smin.htm
// polynomial smooth min (k = 0.1);
float smin(float a, float b, float k)
{
    float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
    return mix(b, a, h) - k * h * (1.0 - h);
}

// https://iquilezles.org/www/articles/distfunctions/distfunctions.htm
float sdf_sphere(vec3 p, float rad)
{
    return length(p) - rad;
}

float sdf_box(vec3 p, vec3 b)
{
    vec3 q = abs(p) - b;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0);
}

float sdf_torus(vec3 p, vec2 t)
{
    vec2 q = vec2(length(p.xz) - t.x, p.y);
    return length(q) - t.y;
}

float sdf_cone(vec3 p, vec2 c)
{
    vec2 q = vec2(length(p.xz), -p.y);
    float d = length(q - c * max(dot(q, c), 0.0));
    return d * (q.x * c.y - q.y * c.x < 0.0 ? -1.0 : 1.0);
}

float world(vec3 p)
{
    float sd = sdf_sphere(p - vec3(0.85, 0.0, 0.0), 1.0);
    float bd = sdf_box(p + vec3(0.85, 0.0, 0.0), vec3(1.0, 1.0, 1.0));

    float d =smin(sd, bd, cos(u_time * 2.0));

    return d;
}

float march(vec3 o, vec3 r)
{
    vec3 p;
    float d, t;

    for (int i = 0; i < 64; i++)
    {
        p = o + r * t;
        d = world(p);
        if (d < 0.01 || t > 100.0) { break; }
        t += d;
    }
    return t;
}

void main()
{
    vec2 uv = vs_pos.xy;
    uv.x /= u_resolution.y / u_resolution.x;
    vec3 rgb;

    vec3 org = vec3(0.0, 0.0, -5.0);
    vec3 ray = normalize(vec3(uv, 1.0));

    float t = march(org, ray);
    if (t < 10.0)
    {
        rgb = (t / 30.0).xxx;
    }

    fs_color = vec4(rgb, 1.0);
}
