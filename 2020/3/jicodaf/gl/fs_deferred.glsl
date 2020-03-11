#version 460

in vec4 vs_pos;
out vec4 fs_color;

uniform vec2 u_res;
uniform float u_aspect;
uniform float u_time;
uniform float u_ispress_0;
uniform float u_ispress_1;
uniform float u_ispress_2;
uniform sampler2D u_screen_tex;

layout(binding=1) uniform sampler2D u_gbuffer_colour;

void main()
{
    vec2 uv = vs_pos.xy * 0.5 + 0.5;

    vec3 rgb = texture(u_gbuffer_colour, uv).xyz;
    rgb = mix(rgb, rgb.xzy, cos(u_time * 3.0) * 0.5 + 0.5);
    float alpha = 1.0 - u_ispress_1;
    fs_color = vec4(rgb * alpha, alpha);
}
