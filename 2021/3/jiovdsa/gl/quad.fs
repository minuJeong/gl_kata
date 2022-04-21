#version 460

in vec4 vs_pos;
out vec4 color;

uniform float u_time;


float hash(vec2 uv) { return fract(cos(dot(uv, vec2(12.4321, 43.41325))) * 43216.643215); }
float hash(float x) { return hash(vec2(x, -x)); }

float smooth_squeeze(float squeeze, float radius, float x)
{
    return smoothstep(squeeze - radius, squeeze + radius, x)
         * smoothstep(squeeze + radius, squeeze - radius, x);
}

vec4 layer_0(vec2 uv)
{
    vec2 vuv = uv * 4.0;
    vec2 coord = floor(vuv);
    vuv = fract(vuv);

    float o = cos(u_time * 7.0 * hash(coord * 2.0)) * 0.2 + 0.3;

    float x = smooth_squeeze(0.35, 0.07, length(vuv * 2.0 - 1.0) - o) > 0.0 ? 1.0 : 0.0;

    vec4 rgb = vec4(x, x, x, 1.0);
    rgb.xyz *= mix(vec3(0.3, 0.8, 0.3), vec3(0.9, 0.1, 0.2), hash(coord));

    return rgb;
}

vec4 layer_1(vec2 uv)
{
    vec2 vuv = (uv + vec2(u_time * 0.24, 0.0)) * 5.0;
    vec2 coord = floor(vuv - vec2(0.5));
    vuv = fract(vuv) * 2.0 - 1.0;
    vec2 vuv_2 = abs(vuv);

    float x = smooth_squeeze(0.0, 0.075, min(vuv_2.x, vuv_2.y)) > 0.0 ? 1.0 : 0.0;
    float rand = hash(coord) * 0.75;
    float alpha = x + rand;

    vec3 rgb = mix(mix(vec3(0.2, 0.6, 0.7), vec3(0.9, 0.3, 0.1), rand), vec3(0.65, 0.64, 0.55), x);

    alpha = clamp(alpha, 0.0, 1.0);
    return vec4(rgb, alpha);
}

vec4 layer_2(vec2 uv)
{
    float alpha_0 = smooth_squeeze(0.0, 0.005, length(uv) - 0.95) > 0.0 ? 1.0 : 0.0;
    float alpha_1 = smooth_squeeze(0.0, 0.010, length(uv) - 0.82) > 0.0 ? 1.0 : 0.0;
    float alpha_2 = smooth_squeeze(0.0, 0.015, length(uv) - 0.54) > 0.0 ? 1.0 : 0.0;

    return vec4(0.72, 0.72, 0.72, max(alpha_0, max(alpha_1, alpha_2)));
}

void main()
{
    vec2 uv = vs_pos.xy;

    vec4 rgb_0 = layer_0(uv);
    vec4 rgb_1 = layer_1(uv);
    vec4 rgb_2 = layer_2(uv);

    vec3 rgb = mix(rgb_0.xyz, rgb_1.xyz, rgb_1.w);
    rgb = mix(rgb, rgb_2.xyz, rgb_2.w);

    vec3 bg = vec3(0.1 - uv.y * 0.08);

    color = vec4(rgb, 1.0);
}
