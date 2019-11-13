#version 460

in vec4 gs_pos;
in vec4 gs_vel;
in vec2 gs_uv;

out vec4 fs_color;

uniform float u_time;

void main()
{
    fs_color = vec4(gs_uv, cos(u_time) * 0.5 + 0.5, 1.0);
}
