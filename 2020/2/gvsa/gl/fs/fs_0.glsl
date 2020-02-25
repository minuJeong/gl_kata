#version 460

in VS_OUT
{
    vec4 vs_local_pos;
    vec4 vs_world_pos;
    vec4 vs_normal;
} vs_out;

out vec4 fs_colour;

uniform mat4 m = mat4(1.0);

void main()
{
    vec3 light_pos = vec3(-10.0, 10.0, -12.0);
    vec3 P = vs_out.vs_world_pos.xyz;
    vec3 N = normalize((m * vs_out.vs_normal).xyz);
    vec3 L = normalize(light_pos - P);

    float lambert = dot(N, L);
    lambert = clamp(lambert, 0.0, 1.0);

    fs_colour = vec4(lambert.xxx, 1.0);
}
