#version 460

in vec2 vs_pos;

out vec4 fs_color;

uniform float u_aspect;
uniform float u_time;


float random(vec2 uv)
{
    highp float x = dot(uv, vec2(12.4321, 45.43215));
    x = mod(x, 3.1415928);
    return fract(sin(x) * 413265.5234143);
}

void main()
{
    vec2 uv = vs_pos;
    uv.x *= u_aspect;
    uv.x += 0.07 * u_time;

    uv *= 6.0;
    vec2 coord = floor(uv);
    uv = fract(uv);

    bool swap = random(coord) < 0.5;
    uv.x = swap ? uv.x : 1.0 - uv.x;

    float t = cos(u_time * 5.5) * 0.5 + 0.5;
    float w = mix(0.1, 0.02, t);
    w = 0.1;

    float x = length(uv);
    x = x - 0.5;
    x = smoothstep(-w, -w + 0.01, x) *
        smoothstep(+w, +w - 0.01, x);

    float ay = atan(uv.y, uv.x);
    uv = 1.0 - uv;

    float y = length(uv);
    y = y - 0.5;
    y = smoothstep(-w, -w + 0.01, y) *
        smoothstep(+w, +w - 0.01, y);

    float ax = atan(uv.y, uv.x);

    x = max(x, y);

    float spd = swap ? -0.5 : 0.5;
    float f = mod(max(ax, ay) + u_time * spd, 1.0);
    f = clamp(f, 0.0, 1.0);

    vec3 c1 = vec3(0.75, 0.25, 0.0);
    vec3 c2 = vec3(0.0, 0.75, 0.15);
    vec3 RGB = smoothstep(c1, c2, vec3(f));

    RGB = clamp(RGB, 0.0, 1.0);
    fs_color = vec4(RGB * x, x);
}
