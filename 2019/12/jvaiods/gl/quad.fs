#version 460

in vec4 vs_pos;
out vec4 fs_color;

uniform sampler2D u_heightmap;

highp float rand(vec2 co)
{
    highp float a = 12.9898;
    highp float b = 78.233;
    highp float c = 43758.5453;
    highp float dt= dot(co.xy ,vec2(a,b));
    highp float sn= mod(dt,3.14);
    return fract(sin(sn) * c);
}

vec3 get_normal(vec2 uv)
{
    const float OFFSET = 0.002;
    float height_tex_L = texture(u_heightmap, uv + vec2(+1.0, 0.0) * OFFSET).x;
    float height_tex_R = texture(u_heightmap, uv + vec2(-1.0, 0.0) * OFFSET).x;
    float height_tex_T = texture(u_heightmap, uv + vec2(0.0, +1.0) * OFFSET).x;
    float height_tex_B = texture(u_heightmap, uv + vec2(0.0, -1.0) * OFFSET).x;

    float dx = height_tex_R - height_tex_L;
    float dy = height_tex_B - height_tex_T;

    vec3 normal = vec3(dx, dy, 0.5) * 0.5 + 0.5;
    return normal;
}

float get_luminosity(vec2 uv)
{
    float x = texture(u_heightmap, uv).x;
    return dot(vec3(x, x, x), vec3(0.2, 0.7, 0.1));
}

void main()
{
    vec2 uv = vs_pos.xy * 0.5 + 0.5;
    uv.y = 1.0 - uv.y;

    float l = get_luminosity(uv);
    fs_color = vec4(l, l, l, 1.0);

    // vec3 normal = get_normal(uv);
    // fs_color = vec4(normal, 1.0);
}
