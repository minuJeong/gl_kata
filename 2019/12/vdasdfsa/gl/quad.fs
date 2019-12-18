#version 460

layout(location=0) in vec4 vs_pos;
layout(location=1) in vec4 vs_uv;
layout(location=2) in vec4 vs_color;
out vec4 fs_color;

uniform float u_time;

float vmax(vec2 xy) { return max(xy.x, xy.y); }
float vmax(vec3 xy) { return max(xy.x, max(xy.y, xy.z)); }
float vmax(vec4 xy) { return max(max(xy.x, xy.y), max(xy.z, xy.w)); }

float sdf_rect(vec2 uv, vec2 b)
{
    return vmax(abs(uv) - b);
}

void main()
{
    vec2 uv = vs_uv.xy;

    float c, s;
    c = cos(u_time);
    s = sin(u_time);
    uv = mat2(c, -s, s, c) * (uv - 0.5);
    float d_rect = sdf_rect(uv, vec2(0.3));
    float x = smoothstep(0.01, -0.01, d_rect);

    vec3 RGB = vs_color.xyz * (x + 0.1);
    fs_color = vec4(RGB, 1.0);
}
