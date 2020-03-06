#version 460

in VS_OUT
{
    vec4 vs_pos;
} vs_out;
out vec4 fs_colour;

float truchet(vec2 uv)
{
    vec2 uv2 = uv * 12.0;
    vec2 coord = floor(uv2);
    uv2 = fract(uv2);

    float x = length(uv2);
    x = smoothstep(0.52, 0.515, x) * smoothstep(0.48, 0.485, x);
    uv2 = 1.0 - uv2;
    float y = length(uv2);
    y = smoothstep(0.52, 0.515, y) * smoothstep(0.48, 0.485, y);

    return x + y;
}

void main()
{
    vec2 uv = vs_out.vs_pos.xy * 0.5 + 0.5;

    vec3 rgb = vec3(uv.y);

    float x = truchet(uv);
    x = clamp(x, 0.0, 0.75);

    fs_colour = vec4(rgb * x, x);
}
