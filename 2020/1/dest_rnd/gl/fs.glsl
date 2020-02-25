#version 460

in vec4 vs_pos;
in vec4 vs_normal;

out vec4 fs_colour;

uniform float u_time;

void main()
{
    vec3 light_pos = vec3(-1.0, 5.0, -2.0);
    light_pos.x = cos(u_time) * 5.0;
    light_pos.z = sin(u_time) * 5.0;

    vec3 N = vs_normal.xyz;
    vec3 L = normalize(light_pos);

    float lambert = dot(N, L);

    fs_colour.xyz = N;
    // fs_colour.xyz = lambert.xxx;
    fs_colour.w = 1.0;
}
