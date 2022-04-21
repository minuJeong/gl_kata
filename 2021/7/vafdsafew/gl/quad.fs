#version 460

struct Voxel
{
    vec3 velocity;
    float pressure;
};

layout(binding=0) buffer b_0
{
    Voxel voxels[];
};

in vec4 vs_pos;
out vec4 fs_color;

uniform float u_time;
uniform vec2 u_resolution;

mat2 get_rot(float x)
{
    float c = cos(x), s = sin(x);
    return mat2(c, s, -s, c);
}

vec3 func_0(vec2 uv)
{
    uv.x += u_time * 0.01;

    float progress = u_time * 2.0;
    uv = get_rot(u_time * length(uv) * -0.01) * uv.xy;
    uv = cos(cos(uv.yx * 4.0));
    float len = -(uv.x * uv.x * uv.x * uv.x + uv.y * uv.y * uv.y * uv.y) * 24.0;
    len /= pow(length(uv), 2.4);

    uv = get_rot(progress + len) * uv.xy;
    return normalize(vec3(uv, 0.33));;
}

float _f(float x) { return 2.0 * x * sin(x) + 1.0; }

vec3 func_1(vec2 uv)
{
    const float e = 0.1;

    uv *= 5.0;

    float x = uv.x, y = uv.y;

    float r = float(abs(_f(x) - y) < e);

    return vec3(float(abs(x) < e) * 0.4, float(abs(y) < e) * 0.4, r);
}

vec3 func_2(vec2 uv)
{
    uv *= 4.0;

    vec2 coord = floor(uv);
    uv = fract(uv);

    float x = mix(0.48, 0.5, uv.x * uv.x + uv.y * uv.y);

    return vec3(x, x, x);
}

void main()
{
    vec2 screen_uv = vs_pos.xy;
    screen_uv.x /= u_resolution.y / u_resolution.x;

    vec2 uv = screen_uv;

    // vec3 rgb = func_0(uv);
    // vec3 rgb = func_1(uv);
    vec3 rgb = func_2(uv);

    fs_color = vec4(rgb, 1.0);
}
