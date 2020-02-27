#version 460

#define NEAR 0.0001
#define FAR 100.0

in VS_OUT
{
    vec4 vs_pos;
} vs_out;

out vec4 fs_colour;

const vec3 UP = vec3(0.0, 1.0, 0.0);

uniform float u_time;
uniform float u_screen_aspect = 1.0;

highp float hash12(vec2 uv)
{
    highp float a = 12.43215;
    highp float b = 45.45321;
    highp float x = dot(uv, vec2(a, b));
    x = mod(x, 3.141592653589793 * 2.0);
    x = sin(x) * 43215.563421;
    return fract(x);
}

float sdf_point(vec3 p) {return length(p);}
float sdf_sphere(vec3 p, float radius) { return sdf_point(p) - radius; }
float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    vec3 d0 = max(d, 0.0);
    vec3 d1 = min(d, 0.0);
    return length(d0) + max(d1.x, max(d1.y, d1.z));
}
float sdf_box(vec3 p, float b) { return sdf_box(p, vec3(b)); }
float op_blend(float a, float b, float r)
{
    vec2 uv = vec2(r - a, r - b);
    uv = max(uv, 0.0);
    return max(min(a, b), r) - length(uv);
}

float sdf_world(vec3 p, out vec3 colour)
{
    float d;
    float time_scale = 4.0;
    float c = cos(u_time * time_scale), s = sin(u_time * time_scale);
    float d_box;
    {
        
        vec3 r = p;

        float W = 2.2;
        vec3 L = vec3(4.0, 1.0, 4.0);

        r -= vec3(1.0, 0.0, 1.0);
        vec3 r_coord = round(r / W);
        r = r - W * clamp(r_coord, -L, L);
        r.xz = mat2(c, -s, s, c) * r.xz;
        r.yz = hash12(r_coord.xy) < 0.5 ? mat2(c, -s, s, c) * r.yz : mat2(s, -c, c, s) * r.yz;
        float size = 0.35;
        d_box = sdf_box(r, size) - size * 0.35;
    }
    d = d_box;

    return d;
}

float march(vec3 o, vec3 r, out vec3 colour)
{
    float t, d;
    vec3 p;
    for (float i = 0.0; i < 1.0; i+=0.002)
    {
        p = o + r * t;
        d = sdf_world(p, colour);
        if (d < NEAR || t > FAR) {break;}
        t += d;
    }
    return t;
}

mat3 look(vec3 o)
{
    vec3 f = normalize(-o);
    vec3 r = cross(f, UP);
    vec3 u = cross(r, f);
    return mat3(r, u, f);
}

vec3 normal_at(vec3 p)
{
    vec3 _c;
    const vec2 e = vec2(NEAR, 0.0);
    return normalize(sdf_world(p, _c) - vec3(
        sdf_world(p - e.xyy, _c),
        sdf_world(p - e.yxy, _c),
        sdf_world(p - e.yyx, _c)
    ));
}

void main()
{
    vec2 st = vs_out.vs_pos.xy;
    vec2 uv = st * 0.5 + 0.5;
    vec3 rgb;

    vec3 o = vec3(-12.0, 18.0, -12.0);
    vec3 r = look(o) * normalize(vec3(st, 1.0));

    vec3 light_pos = vec3(-100.0, 400.0, -200.0);

    float travel = march(o, r, rgb);
    if (travel < FAR)
    {
        vec3 P = o + r * travel;
        vec3 N = normal_at(P);
        vec3 L = normalize(light_pos - P);

        float lambert = dot(N, L);
        lambert = clamp(lambert, 0.05, 1.0);

        rgb += lambert;
    }
    else
    {
        rgb = vec3(0.2 - uv.y * 0.1);
    }

    fs_colour = vec4(rgb, 1.0);
}
