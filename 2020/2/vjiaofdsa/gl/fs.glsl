#version 460

#define NEAR 0.002
#define FAR 100.0

in vec4 vs_pos;
out vec4 fs_colour;

uniform float u_time;
uniform float u_aspect;
uniform sampler2D u_texture;

const vec3 UP = vec3(0.0, 1.0, 0.0);

vec2 g_tex_uv = vec2(0.0, 0.0);

float vmax(vec3 p) { return max(p.x, max(p.y, p.z)); }
float vmax(vec4 p) { return max(max(p.x, p.y), max(p.z, p.w)); }

float sdf_sphere(vec3 p, float r) { return length(p) - r; }
float sdf_box(vec3 p, vec3 b) { vec3 d = abs(p) - b; return length(max(d, 0.0)) + vmax(min(d, 0.0)); }
float sdf_box(vec3 p, float b) { return sdf_box(p, vec3(b)); }

float op_union_round(float a, float b, float r)
{
    vec2 uv = vec2(r - a, r - b);
    uv = max(uv, 0.0);
    return max(r, min(a, b)) - length(uv);
}

float sdf(vec3 p)
{
    float d = 100.0;

    float c = cos(u_time), s = sin(u_time);
    mat2 rotmat = mat2(c, -s, s, c);

    // box
    {
        vec3 q = p;
        q.x -= -2.0;
        
        q.xz = rotmat * q.xz;
        d = sdf_box(q, 1.5) - 0.15;

        if (d < NEAR)
        {
            g_tex_uv = q.xz;

            // displacement
            {
                vec3 q = p * 8.0;
                q.xz = rotmat * q.xz;
                float displacement = sin(q.x) * cos(q.y) * sin(q.z) * pow(0.5, 3);
                d += max(displacement, 0.0);
            }
        }
    }

    // sphere
    {
        rotmat = inverse(rotmat);

        vec3 q = p;
        q.x -= +2.0;
        float d_sphere = sdf_sphere(q, 2.0);
        float r = 0.75;
        d = op_union_round(d_sphere, d, r);

        if (d < NEAR)
        {
            g_tex_uv = mix(rotmat * q.xz, g_tex_uv, clamp(d_sphere - d - r, 0.0, 1.0));

            // displacement
            {
                vec3 q = p * 8.0;
                q.xz = rotmat * q.xz;
                float displacement = sin(q.x) * cos(q.y) * sin(q.z) * pow(0.4, 3);
                d += displacement;
            }
        }
    }

    return d;
}

float march(vec3 o, vec3 r)
{
    vec3 p; float t = 0.5, d = 0.0;
    for (int i = 0; i < 48; i++)
    {
        p = o + r * t; d = sdf(p); t += d;
        if (d < NEAR || t > FAR) { break; }
    }
    return t;
}

mat3 lookz(vec3 o)
{
    vec3 f = normalize(-o);
    vec3 r = cross(f, UP);
    vec3 u = cross(r, f);
    return mat3(r, u, f);
}

vec3 normalat(vec3 p)
{
    const vec2 e = vec2(NEAR, 0.0);
    return normalize(sdf(p) - vec3(sdf(p - e.xyy), sdf(p - e.yxy), sdf(p - e.yyx)));
}

void main()
{
    vec2 uv = vs_pos.xy;
    uv.x *= u_aspect;

    vec3 colour = vec3(0.1 - uv.y * 0.08);
    vec3 light_pos = vec3(-10.0, 10.0, -10.0);
    vec3 o = vec3(0.0, 5.0, -8.0);
    vec3 r = lookz(o) * normalize(vec3(uv, 1.0));

    float t = march(o, r);
    if (t < FAR)
    {
        vec2 texuv = clamp(g_tex_uv * 0.5 + 0.5, 0.0, 1.0);
        vec3 tex_colour = texture(u_texture, texuv).xyz;

        vec3 P = o + r * t;
        vec3 N = normalat(P);
        vec3 L = normalize(light_pos - P);

        float lambert = dot(N, L);
        lambert = max(lambert, 0.0);

        colour = lambert * tex_colour;
    }

    fs_colour = vec4(colour, 1.0);
}
