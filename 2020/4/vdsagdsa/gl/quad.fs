#version 460

in vec4 v2f_pos;
out vec4 fs_colour;

uniform vec2 u_resolution;
uniform float u_time;

layout(binding=0) uniform sampler2D u_tex_0;
layout(binding=1) uniform sampler2D u_tex_1;

highp float hash12(vec2 uv)
{
    highp const vec2 XY = vec2(12.4132, 43.6143);
    highp float x = dot(uv, XY);
    highp float y = sin(x) * 43216.43216;
    return fract(y);
}

void main()
{
    vec2 uv = v2f_pos.xy;
    uv.y = 1.0 - uv.y;

    uv *= 124.0;
    vec2 coord = floor(uv);
    uv = fract(uv);
    uv = uv * 2.0 - 1.0;

    float rotation = hash12(coord.xy) * 4.0 - 2.0;
    float c = cos(rotation), s = sin(rotation);
    uv.xy = mat2(c, -s, s, c) * uv.xy;
    uv = uv * 0.5 + 0.5;

    vec4 tex_0 = texture(u_tex_0, uv);
    vec4 tex_1 = texture(u_tex_1, uv);

    vec3 rgb = mix(tex_0.xyz, tex_1.xyz, tex_1.w);
    // rgb.xy = mix(rgb.xy, uv, 0.1);

    fs_colour = vec4(rgb, 1.0);
}
