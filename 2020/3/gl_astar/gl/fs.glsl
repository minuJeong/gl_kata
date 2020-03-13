#version 460

#define NEAR 0.002
#define FAR 100.0

const vec3 ZERO = vec3(0.0, 0.0, 0.0);
const vec3 UP = vec3(0.0, 1.0, 0.0);

in vec4 vs_pos;
out vec4 fs_colour;

uniform vec2 u_resolution;
uniform vec3 u_campos;
uniform vec3 u_lightpos;

float sdf_sphere(vec3 pos, float radius) { return length(pos) - radius; }
float sdf_box(vec3 pos, vec3 box)
{
    vec3 d = abs(pos) - box;
    vec3 d0 = max(d, 0.0);
    vec3 d1 = min(d, 0.0);
    return length(d0) + max(d1.x, max(d1.y, d1.z));
}
float sdf_box(vec3 pos, float box) { return sdf_box(pos, vec3(box, box, box)); }

float sdf_world(vec3 p)
{
    vec3 q = p;

    float d_sphere = sdf_sphere(q - vec3(2.0, 0.0, 0.0), 2.0);
    float d_box = sdf_box(q - vec3(-2.0, 0.0, 0.0), 2.0);
    float d = min(d_sphere, d_box);

    return d;
}

float march(vec3 o, vec3 r)
{
    vec3 p;
    float t = 0.5, d = 0.0;
    for (float step = 0.0; step < 1.0; step += 1.0 / 128.0)
    {
        p = o + r * t;
        d = sdf_world(p);
        if (d < NEAR || t > FAR) { break; }
        t += d;
    }
    return t;
}

mat3 lookat(vec3 o, vec3 t)
{
    vec3 f = normalize(t - o);
    vec3 r = cross(f, UP);
    vec3 u = cross(r, f);
    return mat3(r, u, f);
}

vec3 normalat(vec3 p)
{
    const vec2 e = vec2(0.002, 0.0);
    return normalize(sdf_world(p) - vec3(
        sdf_world(p - e.xyy),
        sdf_world(p - e.yxy),
        sdf_world(p - e.yyx)
    ));
}

float sdf2d_rect(vec2 uv, vec2 b)
{
    vec2 d = abs(uv) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

void main()
{
    vec2 uv = vs_pos.xy;
    vec2 wuv = uv;
    float aspect = u_resolution.x / u_resolution.y;
    wuv.x *= aspect;

    vec3 campos = u_campos;
    vec3 ray = lookat(u_campos, ZERO) * normalize(vec3(wuv, 1.0));   

    float travel = march(campos, ray);
    vec3 rgb = vec3(0.2, 0.2, 0.2);
    vec3 light_pos = u_lightpos;
    float alpha = 0.1;
    if (travel < FAR)
    {
        vec3 P = campos + ray * travel;
        vec3 N = normalat(P);
        vec3 L = normalize(light_pos - P);

        float lambert = max(dot(N, L), 0.1);
        lambert += max(dot(N, -UP), 0.0) * 0.1;

        rgb = lambert.xxx;
        alpha = 1.0;
    }
    fs_colour = vec4(rgb * alpha, alpha);
}
