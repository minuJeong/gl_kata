#version 460

in vec4 in_pos;
in vec4 in_normal;

out VS_OUT
{
    vec4 vs_local_pos;
    vec4 vs_world_pos;
} vs_out;

uniform mat4 m = mat4(1.0);
uniform float u_time;

void main()
{
    vs_out.vs_local_pos = in_pos;

    vs_out.vs_world_pos = m * vs_out.vs_local_pos;
    gl_Position = vs_out.vs_world_pos;
}
