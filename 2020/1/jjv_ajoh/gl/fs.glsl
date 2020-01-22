#version 460

in vec2 vs_pos;
out vec4 fs_colour;

uniform float u_time;
uniform vec2 u_draginput;
layout(location=0) uniform sampler2D u_texture;

const vec3 ZERO = vec3(0.0);
const vec3 UP = vec3(0.0, 1.0, 0.0);
const vec3 FRONT = vec3(0.0, 0.0, 1.0);


float sdf_sphere(vec3 p, float radius)
{
    return length(p) - radius;
}

float sdf_box(vec3 p, vec3 box)
{
    vec3 b = abs(p) - box;
    vec3 b0 = max(b, 0.0);
    vec3 b1 = min(b, 0.0);
    return length(b0) - max(b1.x, max(b1.y, b1.z));
}

float sdf_plane(vec3 p, vec3 n)
{
    return dot(p, n);
}


float world(vec3 p)
{
    float distance = 100.0;

    // 1
    {
        vec3 q = p - vec3(-1.0, 0.0, 0.0);
        float d = sdf_sphere(q, 1.0);
        distance = min(distance, d);
    }

    // 2
    {
        vec3 q = p - vec3(+1.0, 0.0, 0.0);
        float d = sdf_box(q, vec3(0.65)) - 0.1;
        distance = min(distance, d);
    }

    // 3
    {
        vec3 q = p - vec3(0.0, 1.731, 0.0);
        float d = sdf_plane(q, UP) + 7.0 - texture(u_texture, q.xz * 0.01 - 0.5).x * 6.0;
        distance = min(distance, d);
    }

    return distance;
}

vec4 raymarch(vec3 o, vec3 r)
{
    float d, t;
    vec3 p;
    for (int i = 0; i < 64; i++)
    {
        p = o + r * t;
        d = world(p);
        if (d < 0.0001 || t > 200.0) { break; }
        t += d;
    }
    return vec4(p, t);
}

mat3 lookat(vec3 p, vec3 o)
{
    vec3 f = normalize(o - p);
    vec3 r = cross(f, UP);
    vec3 u = cross(r, f);
    return mat3(r, u, f);
}

vec3 normalat(vec3 p)
{
    const vec2 e = vec2(0.002, 0.0);
    return normalize(world(p) - vec3(
        world(p - e.xyy),
        world(p - e.yxy),
        world(p - e.yyx)
    ));
}

void main()
{
    vec2 uv = vs_pos.xy;

    vec3 RGB = vec3(0.1 - uv.y * 0.03);

    vec3 origin = vec3(-1.6, 4.0, -4.6);
    origin.x = cos(u_time * 0.2) * 5.0;
    origin.z = sin(u_time * 0.2) * 5.0;

    vec3 ray = lookat(origin, vec3(0.0, 0.5, 0.0)) * normalize(vec3(uv, 1.0));

    vec4 march = raymarch(origin, ray);

    float travel = march.w;
    if (travel < 100.0)
    {
        vec3 light_pos = vec3(2.0);
        light_pos.x = cos(-u_draginput.x * 0.003) * 5.0;
        light_pos.y = -u_draginput.y * 0.01;
        light_pos.z = sin(-u_draginput.x * 0.003) * 5.0;

        vec3 P = march.xyz;
        vec3 N = normalat(P);
        vec3 L = normalize(light_pos - P);
        vec3 V = ray;
        vec3 H = normalize(-V + L);

        float blinn = dot(N, H);
        blinn = max(blinn, 0.0);
        blinn = pow(blinn + 0.02, 64.0);
        blinn *= 0.25;

        float fresnel = 1.0 - dot(N, H);
        fresnel = max(fresnel, 0.0);
        fresnel = pow(fresnel, 5.0);
        fresnel *= 0.01;

        float specular = blinn + fresnel;
        vec3 specular_colour = vec3(0.95, 0.91, 0.8) * specular;

        float lambert = (1.0 - specular) * dot(N, L);
        lambert = max(lambert, 0.0);

        float ambient = (1.0 - specular - lambert) * 0.2;

        vec3 diffuse_colour = vec3(0.95, 0.11, 0.77) * (lambert + ambient);

        RGB = specular_colour + diffuse_colour;
    }

    fs_colour = vec4(RGB, 1.0);
}
