#version 460

in vec3 in_pos;

out vec3 vs_pos;

uniform ivec2 u_resolution;

void main()
{
    vs_pos = in_pos;
    vs_pos.x /= u_resolution.x / u_resolution.y;

    gl_Position = vec4(vs_pos, 1.0);
}
