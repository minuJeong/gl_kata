#version 460

in GS_OUT
{
    vec4 gs_local_pos;
    vec4 gs_world_pos;
    vec4 gs_normal;
} gs_out;

out vec4 fs_colour;

uniform vec3 camera_pos = vec3(0.0, 0.0, 0.0);
uniform mat4 m = mat4(1.0);

void main()
{
    vec3 light_pos = vec3(-5.0, 5.0, -10.0);
    vec3 P = gs_out.gs_world_pos.xyz;
    vec3 N = gs_out.gs_normal.xyz;
    vec3 L = normalize(light_pos - P);
    vec3 V = normalize(P - camera_pos);
    vec3 H = normalize(V + L);

    float blinn = dot(N, H);
    blinn = max(blinn, 0.6);
    blinn = pow(blinn, 5.0);

    float lambert = dot(N, L);
    lambert = clamp(lambert, 0.12, 1.0);

    float light = blinn + lambert;

    fs_colour = vec4(light.xxx, 1.0);
}
