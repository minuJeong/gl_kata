#version 460

in vec2 vs_pos;
out vec4 fs_color;

uniform sampler2D u_gbuffer_basecolor;
uniform float u_time;
uniform float u_aspect;

void main()
{
    vec2 uv = vs_pos.xy * 0.5 + 0.5;
    vec4 texcolor_basecolor = texture(u_gbuffer_basecolor, uv);
    vec3 RGB = texcolor_basecolor.xyz;

    uv.x *= u_aspect;
    uv *= 14.0;
    vec2 coord = floor(uv);
    uv = fract(uv);

    float x = mod(coord.x + coord.y, 2.0);
    RGB.y += x * 0.2;

    fs_color = vec4(RGB, 1.0);
}
