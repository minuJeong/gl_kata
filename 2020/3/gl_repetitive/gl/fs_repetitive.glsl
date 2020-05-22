#version 460

#define NEAR 0.002
#define FAR 1000.0

const vec3 ZERO = vec3(0.0, 0.0, 0.0);
const vec3 UP = vec3(0.0, 1.0, 0.0);

in vec4 vs_pos;
out vec4 fs_colour;

uniform vec2 u_resolution;
uniform vec3 u_campos;
uniform vec3 u_lightpos;

uniform bool u_isclicked;
uniform bool u_ismouseover;
uniform vec2 u_mousepos;

uniform float u_time;

float sdf_sphere(vec3 pos, float radius) { return length(pos) - radius; }
float sdf_box(vec3 pos, vec3 box)
{
    vec3 d = abs(pos) - box;
    vec3 d0 = max(d, 0.0);
    vec3 d1 = min(d, 0.0);
    return length(d0) + max(d1.x, max(d1.y, d1.z));
}
float sdf_box(vec3 pos, float box) { return sdf_box(pos, vec3(box, box, box)); }

void fin_repeat(inout vec3 p, vec3 c, vec3 n)
{
    return p - c * clamp(round(p / c), -n, n);
}

void fin_repeat(inout vec3 p, float c, float n) { fin_repeat(p, vec3(c), n); }
void fin_repeat(inout vec3 p, vec3 c, float n) { fin_repeat(p, c, vec3(n)); }
void fin_repeat(inout vec3 p, float c, float n) { fin_repeat(p, vec3(c), vec3(n)); }

float sdf_world(vec3 p)
{
    vec3 q = p;

    float w = 10.0;
    float n = 1.0;
    fin_repeat(q, w, n);

    float d_sphere = sdf_sphere(q - vec3(2.0, 0.0, 0.0), 2.0);
    float c = cos(u_time), s = sin(u_time);
    q.xz = mat2(c, -s, s, c) * (q.xz - vec2(-2.0, 0.0));
    float d_box = sdf_box(q, 1.5) - 0.1;
    float d = min(d_sphere, d_box);

    return d;
}

vec2 march(vec3 o, vec3 r)
{
    vec3 p;
    float t = 0.5, d = 0.0;
    float n_steps = 0.0;
    for (;n_steps < 128.0; n_steps += 1.0)
    {
        p = o + r * t;
        d = sdf_world(p);
        if (d < NEAR || t > FAR) { break; }
        t += d;
    }
    return vec2(t, n_steps);
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

    float travel = march(campos, ray).x;
    vec3 rgb = vec3(0.2, 0.2, 0.2);
    vec3 light_pos = u_lightpos;
    float alpha = 0.5;
    if (travel < FAR)
    {
        vec3 P = campos + ray * travel;
        vec3 N = normalat(P);
        vec3 L = normalize(light_pos - P);

        float lambert = max(dot(N, L), 0.1);
        lambert += max(dot(N, -UP), 0.0) * 0.1;

        vec2 shadow = march(P, L);
        float dist_light = length(P - light_pos);
        lambert *= step(dist_light, shadow.x) * 0.3 + 0.7;

        rgb = lambert.xxx;
        alpha = 1.0;
    }

    fs_colour = vec4(rgb * alpha, alpha);
}
