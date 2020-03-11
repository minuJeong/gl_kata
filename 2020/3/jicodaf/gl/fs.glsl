#version 460

in vec4 vs_pos;
out vec4 fs_color;

uniform vec2 u_res;
uniform float u_aspect;
uniform float u_time;
uniform float u_ispress_0;
uniform float u_ispress_1;
uniform float u_ispress_2;

layout(binding=0) uniform sampler2D u_screen_tex;
layout(binding=1) uniform sampler2D u_gbuffer_colour;


float border_0(vec2 xy)
{
    vec2 res = u_res;
    vec2 border = vec2(5.0);
    xy = step(xy.xy, border) + step(-xy.xy, border - res.xy);
    return max(xy.x, xy.y) * 0.5;
}

void main()
{
    vec2 uv = vs_pos.xy * 0.5 + 0.5;
    vec2 xy = uv * u_res.xy;

    float x = border_0(xy);

    vec2 tuv = uv;
    vec4 gbuffer_colour = texture(u_gbuffer_colour, tuv);

    // imageio screen capture is y-flipped
    tuv = uv * vec2(1, -1);
    vec4 texcolor = texture(u_screen_tex, tuv);

    vec3 rgb = mix(gbuffer_colour.xyz, texcolor.xyz, 0.15);
    rgb = mix(rgb, vec3(1,0,0), x);

    float alpha = u_ispress_1 > 0.5 ? 0.0 : 1.0;
    alpha += x;
    fs_color = vec4(rgb * alpha, alpha);
}
