#version 460

in vec2 vs_position;
out vec4 fs_color;

uniform vec2 u_resolution;

void main()
{
    vec2 uv = vs_position;
    uv.x *= u_resolution.x / u_resolution.y;

    float distance = length(uv);
    float angle = atan(uv.y, uv.x);
    float diff = uv.y - uv.x;

    vec3 color = vec3(1.0, 1.0, 1.0);

    float is_valid_distance =
        smoothstep(0.01, 0.02, mod(diff, 0.07)) *
        smoothstep(0.03, 0.02, mod(diff, 0.07));
    color = is_valid_distance.xxx;

    fs_color = vec4(color, 1.0);
}
