#version 460

in VS_OUT
{
    vec4 vs_local_pos;
    vec4 vs_world_pos;
    vec4 vs_normal;
} vs_out;

out vec4 fs_colour;

void main()
{
    vec3 light_pos = vec3(-10.0, 10.0, -12.0);
    vec3 P = vs_out.vs_world_pos.xyz;
    vec3 N = vs_out.vs_normal.xyz;
    vec3 L = normalize(light_pos - P);

    float lambert = dot(N, L);
    lambert = lambert * 0.5 + 0.5;

    fs_colour = vec4(lambert, lambert, lambert, 1.0);
}
