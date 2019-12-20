#version 460

layout(location=0) in vec4 vs_pos;
layout(location=1) in vec4 vs_uv;
layout(location=2) in vec4 vs_color;

layout(location=0) out vec4 fs_basecolor;
layout(location=1) out vec4 fs_brightcolor;

uniform float u_time;

float vmax(vec2 xy) { return max(xy.x, xy.y); }
float vmax(vec3 xy) { return max(xy.x, max(xy.y, xy.z)); }
float vmax(vec4 xy) { return max(max(xy.x, xy.y), max(xy.z, xy.w)); }

float sdf_rect(vec2 uv, vec2 b)
{
    vec2 d = abs(uv) - b;
    return length(max(d, 0.0));
}

void main()
{
    vec2 uv = vs_uv.xy;

    float c, s;
    c = cos(u_time * 3.14);
    s = sin(u_time * 3.14);
    uv = mat2(c, -s, s, c) * (uv - 0.5);

    float d_rect = sdf_rect(uv, vec2(0.15)) - 0.15;
    d_rect = abs(d_rect) - 0.04;

    float x = smoothstep(0.01, -0.01, d_rect);

    vec3 RGB = vs_color.xyz * x;
    fs_basecolor = vec4(RGB, x);

    bool isbright = dot(RGB, vec3(0.2126, 0.7152, 0.0722)) > 1.0;
    fs_brightcolor = isbright ? vec4(RGB, x) : vec4(0.0, 0.0, 0.0, 0.0);
}
