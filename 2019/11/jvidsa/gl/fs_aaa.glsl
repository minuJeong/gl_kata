#version 460

in vec2 vs_pos;
out vec4 fs_color;

uniform float u_time;
uniform float u_aspect = 1.0;


float vmax(vec2 xy)
{
    return max(xy.x, xy.y);
}

float vmax(vec3 xyz)
{
    return max(max(xyz.x, xyz.y), xyz.z);
}


float sdf_sphere(vec3 p, float radius)
{
    return length(p) - radius;
}

float sdf_box(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    return max(d.x, max(d.y, d.z));
}

float sdf_box_expensive(vec3 p, vec3 b)
{
    vec3 d = abs(p) - b;
    return length(max(d, 0.0)) + vmax(min(d, 0.0));
}

float op_union_round(float a, float b, float r)
{
    vec2 uu = max(vec2(r - a, r - b), vec2(0.0));
    return max(min(a, b), r) - length(uu);
}

float sdf(vec3 p)
{
    float d_sphere = sdf_sphere(p - vec3(-1.0, 0.0, 0.0), 1.0);
    float d_box = sdf_box_expensive(p - vec3(1.0, 0.0, 0.0), vec3(0.8)) - 0.2;

    return op_union_round(d_sphere, d_box, 0.5);
}

float raymarch(vec3 o, vec3 r)
{
    vec3 p;
    float t, d;

    for (int i = 0; i < 48; i++)
    {
        p = o + r * t;
        d = sdf(p);
        if (d < 0.002 || t > 50.0)
        {
            break;
        }
        t += d;
    }

    return t;
}

vec3 normal_at(vec3 p)
{
    const vec2 e = vec2(0.002, 0.0);

    float dx = sdf(p + e.xyy) - sdf(p - e.xyy);
    float dy = sdf(p + e.yxy) - sdf(p - e.yxy);
    float dz = sdf(p + e.yyx) - sdf(p - e.yyx);

    return normalize(vec3(dx, dy, dz));
}

mat3 lookat(vec3 o, vec3 to)
{
    vec3 ws_up = vec3(0.0, 1.0, 0.0);
    vec3 forward = normalize(to - o);
    vec3 right = cross(forward, ws_up);
    vec3 ls_up = cross(right, forward);
    return mat3(right, ls_up, forward);
}

void main()
{
    float xz_rotation = u_time * 2.0;

    vec3 camera = vec3(-5.0, 5.0, -5.0);
    camera.x = cos(xz_rotation) * 5.0;
    camera.z = sin(xz_rotation) * 5.0;

    vec2 uv = vs_pos;
    uv.x *= u_aspect;

    vec3 ray = lookat(camera, vec3(0.0)) * normalize(vec3(uv, 1.0));

    vec3 RGB = vec3(0.1 - vs_pos.y * 0.1);
    float t = raymarch(camera, ray);
    if (t < 50.0)
    {
        vec3 P = camera + ray * t;
        vec3 N = normal_at(P);
        vec3 L = normalize(vec3(-2.0, 2.0, -2.0));
        vec3 H = normalize(L - ray);

        float blinn = dot(N, H);
        blinn = pow(max(blinn, 0.0), 128.0);

        float fresnel = 1.0 - max(dot(N, -ray), 0.0);
        fresnel = pow(fresnel, 5.0);

        float lambert = max(dot(N, L), 0.0);

        float specular = blinn + fresnel;
        float diffuse = (1.0 - specular) * lambert;

        float light = specular + diffuse;

        RGB = light.xxx;
    }

    fs_color = vec4(RGB, 1.0);
}
