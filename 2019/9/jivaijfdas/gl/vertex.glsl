#version 460

in vec4 in_pos;
out vec2 vs_pos;
out vec2 vs_uv;

uniform float u_width;
uniform float u_height;

void main()
{
    vs_pos = in_pos.xy;
    vec2 uv = in_pos.xy;

    float aspect = u_width / u_height;
    uv.x *= aspect;

    uv = uv * 0.5 + 0.5;
    vs_uv = uv;

    gl_Position = vec4(vs_pos, 0.0, 1.0);
}
