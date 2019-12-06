#version 460

in vec4 in_position;
in vec4 in_velocity;
in vec4 in_color;

out VS_OUT
{
    vec4 position;
    vec4 velocity;
    vec4 color;
} vs_out;

uniform mat4 u_mvp = mat4(1.0);

void main()
{
    vs_out.position = in_position;
    vs_out.velocity = in_velocity;
    vs_out.color = in_color;
    gl_Position = u_mvp * in_position;
}
