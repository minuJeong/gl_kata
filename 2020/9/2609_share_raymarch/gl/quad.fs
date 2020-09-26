#version 460

in vec4 vs_pos;
out vec4 fs_color;

uniform vec2 u_resolution;
uniform float u_time;

float smooth_min(float a, float b, float k)
{
    float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
    return mix(b, a, h) - k * h * (1.0 - h);
}

float sdf_sphere(vec3 position, float radius)
{
    return length(position) - radius;
}

float sdf_box(vec3 position, vec3 box)
{
    vec3 relative_position = abs(position) - box;
    float max_yz = max(relative_position.y, relative_position.z);
    float max_xyz = max(relative_position.x, max_yz);
    float rel_pos_length = length(max(relative_position, 0.0));
    return rel_pos_length + min(max_xyz, 0.0);
}

float sdf_world(vec3 position)
{
    float dist_sphere = sdf_sphere(position - vec3(-0.75, 0.0, 0.0), 1.0);
    vec3 q = position - vec3(0.75, 0.0, 0.0);

    float rotation = u_time * -2.0;
    float s = sin(rotation), c = cos(rotation);
    q.xz = mat2(c, -s, s, c) * q.xz;
    q.zy = mat2(c, -s, s, c) * q.zy;
    float dist_box = sdf_box(q, vec3(0.7, 0.7, 0.7));
    dist_box -= 0.2;

    return smooth_min(dist_sphere, dist_box, 0.5);
}

float raymarch(vec3 camera_position, vec3 ray)
{
    vec3 position;
    float distance, travel;
    for (int step = 0; step < 64; step++)
    {
        position = camera_position + ray * travel;
        distance = sdf_world(position);
        if (distance < 0.01 || travel > 100.0) { break; }
        travel += distance;
    }
    return travel;
}

vec3 normal_at(vec3 position)
{
    vec2 epsilon = vec2(0.01, 0.0);
    return normalize(
        sdf_world(position) - vec3(
            sdf_world(position - epsilon.xyy),
            sdf_world(position - epsilon.yxy),
            sdf_world(position - epsilon.yyx)
        )
    );
}

mat3 lookat(vec3 camera_position, vec3 focus_position)
{
    vec3 forward = normalize(focus_position - camera_position);
    vec3 right = cross(forward, vec3(0.0, 1.0, 0.0));
    vec3 up = cross(right, forward);
    return mat3(right, up, forward);
}

void main()
{
    vec2 uv = vs_pos.xy;
    uv.y /= u_resolution.x / u_resolution.y;

    vec3 camera_position = vec3(0.0, 0.0, 0.0);
    camera_position.y = 2.0;
    camera_position.x = cos(u_time) * 5.0;
    camera_position.z = sin(u_time) * 5.0;

    vec3 ray = lookat(camera_position, vec3(0.0, 0.0, 0.0)) * normalize(vec3(uv, 1.0));

    vec3 rgb = vec3(0.0, 0.0, 0.0);

    float travel = raymarch(camera_position, ray);
    if (travel < 50.0)
    {
        vec3 P = camera_position + ray * travel;
        vec3 N = normal_at(P);
        vec3 L = normalize(vec3(-1.0, 1.0, -1.0));

        float lambert = dot(N, L);
        lambert = max(lambert, 0.05);
        rgb = lambert.xxx;
    }

    fs_color = vec4(rgb, 1.0);
}
