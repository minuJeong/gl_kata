#version 460

in vec2 vs_pos;
out vec4 fs_color;

layout(location=0) uniform sampler2D u_gbuffer_basecolor;
layout(location=1) uniform sampler2D u_bloomtex;

uniform float u_time;
uniform float u_aspect;

void main()
{
    vec2 uv = vs_pos.xy * 0.5 + 0.5;
    vec4 texcolor_basecolor = texture(u_gbuffer_basecolor, uv);
    vec4 texcolor_brightcolor = texture(u_bloomtex, uv);

    vec3 RGB = texcolor_basecolor.xyz + texcolor_brightcolor.xyz;

    RGB = texture(u_bloomtex, uv).xyz;
    fs_color = vec4(RGB, 1.0);
}
