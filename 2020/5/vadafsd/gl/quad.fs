#version 460

in vec4 vs_pos;
out vec4 fs_color;

uniform vec2 u_resolution;
uniform float u_time;

float hash12(vec2 uv)
{
    return fract(cos(dot(uv, vec2(12.34214, 43.654321))) * 43215.43215);
}

void main()
{
    vec3 rgb = vec3(0.0);
    vec2 uv = vs_pos.xy * 0.5 + 0.5;

    uv.x += u_time * 0.06;

    uv.x *= u_resolution.x / u_resolution.y;

    float alpha = 1.0;

    uv *= 12.0;
    vec2 xy = floor(uv);
    uv = fract(uv);
    uv.x = hash12(xy) < 0.5 ? uv.x : 1.0 - uv.x;

    float x = uv.x + uv.y;
    x = step(x, 0.7) * step(0.3, x);

    uv = 1.0 - uv;
    float y = uv.x + uv.y;
    y = step(y, 0.7) * step(0.3, y);

    rgb = vec3(max(x, y));

    fs_color = vec4(rgb, alpha);
}
