#version 460

in vec4 vs_pos;
out vec4 fs_colour;

float sdf_sphere(vec3 p, float radius)
{
    return length(p) - radius;
}

float sdf_world(vec3 p)
{
    return sdf_sphere(p - vec3(0.0, 0.0, 5.0), 2.0);
}

float raymarch(vec3 origin, vec3 direction)
{
    vec3 cursor = origin;
    float distance = 0.0, step_distance = 0.0;
    for (int i = 0; i < 64; i++)
    {
        cursor = origin + direction * step_distance;
        step_distance = sdf_world(cursor);
        if (step_distance < 0.01 || distance > 100.0) { break; }
        distance += step_distance;
    }
    return distance;
}

vec3 normal_at(vec3 p)
{
    const vec2 e = vec2(0.02, 0.0);
    return normalize(sdf_world(p) - vec3(
        sdf_world(p - e.xyy),
        sdf_world(p - e.yxy),
        sdf_world(p - e.yyx)
    ));
}

void main()
{
    vec2 uv = vs_pos.xy;
    vec3 rgb = vec3(0.0);

    vec3 origin = vec3(0.0, 0.0, 0.0);
    vec3 direction = normalize(vec3(uv, 1.0));

    float distance = raymarch(origin, direction);
    vec3 light = normalize(vec3(-100.0, 100.0, 100.0));
    if (distance < 100.0)
    {
        vec3 position = origin + direction * distance;
        vec3 normal = normal_at(position);
        float lambert = dot(-normal, -light);
        lambert = abs(lambert);
        rgb = lambert.xxx;
    }

    fs_colour = vec4(rgb, 1.0);
}
