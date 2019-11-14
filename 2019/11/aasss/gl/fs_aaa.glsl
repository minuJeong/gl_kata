#version 460

in vec2 vs_pos;

out vec4 fs_color;

uniform float u_time;


float sdf_sphere(vec3 p, float radius)
{
    return length(p) - radius;
}

float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    vec3 d1 = max(d, 0.0);
    vec3 d2 = min(d, 0.0);
    return length(d1) + max(max(d2.x, d2.y), d2.z);
}

float op_union_round(float a, float b, float t)
{
    vec2 uu = max(vec2(t - a, t - b), 0.0);
    return max(min(a, b), t) - length(uu);
}

float sdf(vec3 p, bool material)
{
    vec3 p_sphere = p - vec3(cos(u_time * 2.0) * 0.5 - 0.4, 0.0, 0.0);
    float d_sphere = sdf_sphere(p_sphere, 0.75);

    vec3 p_box = p - vec3(0.4, 0.0, 0.0);
    float c = cos(u_time * 0.8);
    float s = sin(u_time * 0.8);
    p_box.xz = mat2(c, -s, s, c) * p_box.xz;
    float d_box = sdf_box(p_box, vec3(0.65)) - 0.04;

    float d = op_union_round(d_sphere, d_box, 0.5);

    if (!material)
    {
        return d;
    }
    return d;
}

float raymarch(vec3 o, vec3 r)
{
    vec3 p;
    float t, d;

    for (int i = 0; i < 64; i++)
    {
        p = o + r * t;
        d = sdf(p, true);

        if (d < 0.002 || t > 100.0)
        {
            break;
        }
        t += d;
    }
    return t;
}

vec3 normal_at(vec3 p)
{
    vec2 e = vec2(0.002, 0.0);
    vec2 tuv;
    return normalize(vec3(
        sdf(p + e.xyy, false) - sdf(p - e.xyy, false),
        sdf(p + e.yxy, false) - sdf(p - e.yxy, false),
        sdf(p + e.yyx, false) - sdf(p - e.yyx, false)
    ));
}

mat3 lookat(vec3 o, vec3 to)
{
    vec3 ws_up = vec3(0.0, 1.0, 0.0);
    vec3 front = normalize(to - o);
    vec3 right = cross(front, ws_up);
    vec3 ls_up = cross(right, front);
    return mat3(right, ls_up, front);
}

vec2 get_uv(vec3 p, vec3 n)
{
    float nu = dot(n, vec3(0.0, 1.0, 0.0));
    vec3 p1 = lookat(vec3(0.0), n) * p;
    return mix(p1.xy, p.xz, nu);
}

float pattern_1(vec2 uv)
{
    vec2 x1 = smoothstep(0.05, 0.05, uv);
    vec2 x2 = smoothstep(0.95, 0.96, uv);
    return max(x1.x, x1.y) + max(x2.x, x2.y);
}

float pattern_2(vec2 uv)
{
    float d = abs(uv.x - uv.y);
    return smoothstep(0.05, 0.04, d);
}

void main()
{
    vec3 o = vec3(0.0, 2.0, 0.0);
    o.x = cos(u_time * 0.5) * 3.0;
    o.z = sin(u_time * 0.5) * 3.0;

    vec3 r = lookat(o, vec3(0.0)) * normalize(vec3(vs_pos, 1.0));

    vec3 RGB = vec3(0.1 - vs_pos.y * 0.05);
    float t = raymarch(o, r);
    if (t < 100.0)
    {
        vec3 P = o + r * t;
        vec3 N = normal_at(P);
        vec3 L = normalize(vec3(-2.0, 2.0, -2.0));
        vec3 H = normalize(L - r);

        float blinn = dot(N, H);
        blinn = max(blinn, 0.0);
        blinn = pow(blinn + 0.002, 512.0);
        blinn = min(blinn, 1.0);

        float fresnel = 1.0 - dot(N, -r);
        fresnel = pow(fresnel, 5.0);

        float lambert = dot(N, L);
        lambert = max(lambert, 0.0);

        float specular = blinn + fresnel;
        float diffuse = (1.0 - specular) * lambert;
        float ambient = (1.0 - diffuse) * 0.15;

        float floor_light = dot(N, vec3(0.0, -1.0, 0.0));
        floor_light = max(floor_light, 0.0);
        ambient += floor_light * 0.25;

        float light = specular + diffuse + ambient;

        vec2 tuv = get_uv(P, N);
        tuv = fract(tuv * 4.0);

        float patterned = 0.0;
        patterned += pattern_1(tuv);
        patterned += pattern_2(tuv);

        RGB = light.xxx * max(patterned, 0.75);
    }

    fs_color = vec4(RGB, 1.0);
}
