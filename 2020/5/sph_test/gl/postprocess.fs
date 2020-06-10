#version 460

in vec4 vs_pos;
out vec4 fs_color;

layout(location=0) uniform sampler2D gb_color;


float gb_at(vec2 uv)
{
    vec4 texcol = texture(gb_color, uv);
    float x = length(texcol.xyz);
    return x;
}

void main()
{
    vec2 uv = vs_pos.xy * 0.5 + 0.5;
    vec3 rgb = vec3(0.0);
    float alpha = 0.0;

    const vec2 e = vec2(0.002, 0.0);
    float x = gb_at(uv);
    float dx = x - gb_at(uv - e.xy);
    float dy = x - gb_at(uv - e.yx);
    vec3 N = normalize(vec3(dx, dy, 1.0));

    x = smoothstep(0.02, 0.12, x);
    rgb = mix(vec3(0.2, 0.23, 0.32), vec3(0.34, 0.7, 0.8), x);
    rgb *= max(dot(N, normalize(vec3(3, 4, 5))), 0.0);

    // DEBUG
    rgb = texture(gb_color, uv).xyz;

    fs_color = vec4(rgb, 1.0);
}
