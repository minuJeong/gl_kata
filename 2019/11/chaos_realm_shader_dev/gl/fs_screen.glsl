#version 460
#define SCALE 3.0
#define OCTAVE 6

in vec4 vs_pos;
in vec2 vs_texcoord;
out vec4 fs_color;

uniform float u_time;
uniform float u_aspect;
layout(location=0) uniform sampler2D u_noisecache;

float random(vec2 uv)
{
    return fract(sin(dot(uv, vec2(12.4321, 56.7664))) * 46421.45321);
}

float noise(vec2 uv)
{
    vec2 coord = floor(uv);
    uv = fract(uv);

    float a = random(coord);
    float b = random(coord + vec2(1.0, 0.0));
    float c = random(coord + vec2(0.0, 1.0));
    float d = random(coord + vec2(1.0, 1.0));

    uv = uv * uv * (3.0 - 2.0 * uv);
    return mix(a, b, uv.x) + (c - a) * uv.y * (1.0 - uv.x) + (d - b) * uv.x * uv.y;
}


float truchet(vec2 uv, float scale)
{
    uv = uv * scale;

    vec2 coord = floor(uv);
    uv = fract(uv);

    float d = random(coord) - 0.5;
    bool r = d < 0.0;
    uv.x = r ? uv.x : 1.0 - uv.x;

    float x = min(length(uv), length(1.0 - uv));

    float LINE = 0.15;
    x = smoothstep(0.5+LINE, 0.5-LINE, x) * smoothstep(0.5-LINE, 0.5+LINE, x);
    return x;
}

float fbm(vec2 uv)
{
    float res = 0.0;
    float amp = 0.5;
    
    for (int i = 0; i < OCTAVE; ++i)
    {
        res += noise(uv) * amp;
        uv *= 2.0;
        amp *= 0.5;
    }

    return res;
}

void preview_fbm_full()
{
    vec2 UV = vs_pos.xy;
    UV.x *= u_aspect;
    UV *= 4.0;

    float x, y;
    {
        vec2 t = u_time * vec2(0.12, 0.05);
        vec2 q, r;

        vec2 uv = UV;
        uv *= SCALE;

        q.x = fbm(uv.xy);
        q.y = fbm(uv.yx);

        y = fbm(uv + q + t);

        t *= 2.851;
        r = vec2(y, 1.0 - y);

        x = fbm(uv + r + t);
    }
    vec3 c0 = vec3(12.25, 6.26, 1.6);
    vec3 c1 = vec3(0.0, 0.05, 0.36);

    x = x * x;
    vec3 RGB = c0 * x + c1 * (1.0 - x);
    RGB = RGB / (1.0 + RGB);

    RGB = clamp(RGB, 0.0, 1.0);
    fs_color = vec4(RGB, 1.0);
}

void preview_fbm()
{
    vec2 UV = vs_pos.xy;
    UV.x *= u_aspect;
    float x = fbm(UV * SCALE);
    fs_color = vec4(x, x, x, 1.0);
}

void preview_fbm_with_tilable()
{
    vec2 UV = vs_pos.xy;
    UV.x *= u_aspect;
    UV.x += u_time * 0.1;

    float x = fbm(UV * 20.0);
    fs_color = vec4(x, x, x, 1.0);
}

void preview_using_noisecache()
{
    vec2 UV = vs_pos.xy * 0.5 + 0.5;
    vec4 texcolor = texture(u_noisecache, UV);

    fs_color.xyz = texcolor.xyz;
    fs_color.w = 1.0;
}

void preview_stackfbm_using_noisecache()
{
    vec2 UV = vs_pos.xy * 0.3;
    UV.x -= u_time * 0.0002;

    float c = cos(u_time);
    float s = sin(u_time);

    float x, y;
    {
        vec2 t = u_time * vec2(0.005, -0.005);
        vec2 q, r;

        vec2 uv = UV;
        uv *= 0.6;

        q.x = texture(u_noisecache, uv.xy / SCALE).x;
        q.y = 1.0 - q.x;
        q /= SCALE * 8.0;

        r.x = texture(u_noisecache, uv + q).x;
        r.y = 30.0 - r.x;
        r /= SCALE * 12.0;

        vec2 xuv = uv + r + t;
        x = texture(u_noisecache, xuv).x;
    }

    vec3 c0 = vec3(12.25, 6.26, 1.6);
    vec3 c1 = vec3(0.0, 0.05, 0.36);

    x = pow(x, 2.22);
    vec3 RGB = c0 * x + c1 * (1.0 - x);
    RGB = RGB / (1.0 + RGB);

    RGB = clamp(RGB, 0.0, 1.0);
    fs_color = vec4(RGB, 1.0);
}

void main()
{
    // preview_fbm();
    // preview_using_noisecache();

    // preview_fbm_with_tilable();
    // preview_fbm_full();
    preview_stackfbm_using_noisecache();
}
