#version 460

#define NEAR 0.01
#define FAR 1024

in struct VS_OUT
{
    vec4 pos;
} vs_out;
out vec4 fs_color;

uniform vec2 u_resolution = vec2(8, 6);
uniform float u_time = 0.0;
uniform float u_camera_rotation_xz = 0.0;
uniform float u_camera_zoom = 1.0;

float smin(float a, float b, float k)
{
    float x = ((a - b) / k) * 0.5 + 0.5;
    float h = clamp(x, 0.0, 1.0);
    return mix(a, b, h) - k * h * (1.0 - h);
}

float sdf_plane(vec3 p, vec3 normal, float distance)
{
    return dot(p, normalize(normal)) - distance;
}

float sdf_box(vec3 p, vec3 box)
{
    vec3 b = abs(p) - box;
    vec3 b0 = max(b, vec3(0.0));
    return length(b0) + min(max(b.x, max(b.y, b.z)), 0.0);
}

float sdf_sphere(vec3 p, float radius)
{
    return length(p) - radius;
}

float sdf_world(vec3 p)
{
    float d_floor = sdf_plane(p, vec3(0.0, 1.0, 0.0), -3.0);

    float d_objects;
    {
        float d_cube = sdf_box(p - vec3(2.0, 0.0, 0.0), vec3(1.5)) - 0.5;

        float d_sphere = sdf_sphere(p - vec3(-2.0, 0.0, 0.0), 2.0);

        d_objects = smin(d_cube, d_sphere, 1.0);
    }

    return min(d_floor, d_objects);
}

float march(vec3 o, vec3 r)
{
    float d = 0.0, t = 0.1;
    for (int i = 0; i < 128; i++)
    {
        d = sdf_world(o + r * t);
        if (d < NEAR || t > FAR) { break; }
        t += d;
    }
    return t;
}

mat3 lookat(vec3 camera, vec3 camera_to)
{
    const vec3 UP = vec3(0.0, 1.0, 0.0);
    vec3 forward = normalize(camera_to - camera);
    vec3 right = cross(forward, UP);
    vec3 local_up = cross(right, forward);
    return mat3(right, local_up, forward);
}

vec3 normal_at(vec3 pos)
{
    const vec2 e = vec2(0.001, 0.0);
    return normalize(sdf_world(pos) - vec3(
        sdf_world(pos - e.xyy),
        sdf_world(pos - e.yxy),
        sdf_world(pos - e.yyx)
    ));
}

// https://iquilezles.org/www/articles/rmshadows/rmshadows.htm
float softshadow( in vec3 ro, in vec3 rd, float mint, float maxt, float k )
{
    float res = 1.0;
    float ph = 1e20;
    for (float t = mint; t < maxt;)
    {
        float h = sdf_world(ro + rd * t);
        if(h < NEAR)
        {
            return 0.0;
        }
        float y = h * h / (2.0 * ph);
        float d = sqrt(h * h - y * y);
        res = min(res, k * d / max(0.0,t - y));
        ph = h;
        t += h;
    }
    return res;
}

void main()
{
    vec2 uv = vs_out.pos.xy;
    uv.x /= u_resolution.y / u_resolution.x;
    vec3 rgb = vec3(0.0);

    vec3 camera = vec3(0.0);
    camera.y = 6.0;
    camera.x = sin(-u_camera_rotation_xz) * 9.0;
    camera.z = cos(-u_camera_rotation_xz) * 9.0;

    vec3 ray = lookat(camera, vec3(0.0, 0.8, 0.0)) * normalize(vec3(uv, u_camera_zoom));

    float distance = march(camera, ray);
    if (distance < FAR)
    {
        const vec3 light_pos = vec3(5, 17, 6);
        vec3 pos = camera + ray * distance;
        const vec3 light_dir = normalize(light_pos - pos);
        vec3 normal = normal_at(pos);
        vec3 half_dir = normalize(light_dir - ray);

        float specular = dot(normal, half_dir);
        specular = max(specular, 0.0);
        specular = pow(specular, 128.0);

        float fresnel = 1.0 - dot(-ray, normal);
        fresnel = max(fresnel, 0.0);
        fresnel = pow(fresnel, 5.0);
        vec3 specular_color = specular * vec3(1.0) + (fresnel * 0.3) * vec3(0.2, 0.5, 1.0);

        float lambert = (1.0 - specular) * dot(normal, light_dir);
        lambert = max(lambert, 0.0);

        vec3 diffuse = lambert * vec3(0.5);
        vec3 ambient = vec3(0.03, 0.02, 0.05);

        vec3 lighting = specular_color + max(diffuse, ambient);

        float shadow = softshadow(pos, light_dir, 0.5, FAR, 12);
        lighting = mix(lighting, lighting * shadow, 0.9);

        rgb = lighting;
    }

    fs_color = vec4(rgb, 1.0);
}
