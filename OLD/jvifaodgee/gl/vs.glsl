#version 460

uniform mat4 u_MVP;

in uint in_index;
in vec3 in_pos;
in vec3 in_normal;

out uint vs_index;
out vec3 vs_pos;
out vec3 vs_normal;

void main()
{
    vec4 pos = u_MVP * vec4(vs_pos, 1.0);

    vs_index = in_index;
    vs_pos = pos.xyz;
    vs_normal = in_normal;

    gl_Position = pos;
}
