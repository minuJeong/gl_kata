#version 460
#define SCALE 4.3
#define OCTAVE 5

in vec4 vs_pos;
in vec2 vs_texcoord;
out vec4 fs_color;

uniform float u_time;
uniform float u_aspect;

float random(vec2 uv)
{
    return fract(sin(dot(uv, vec2(12.4321, 56.7664))) * 53421.45321);
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

    // coord.x += u_time * 0.5e-6;

    float d = random(coord) - 0.5;
    bool r = d < 0.0;
    uv.x = r ? uv.x : 1.0 - uv.x;

    float x = min(length(uv), length(1.0 - uv));

    float LINE = 0.24;
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

float stack_fbm(vec2 uv, float scale)
{
    uv *= scale;

    vec2 t = u_time * vec2(0.21, 0.23);

    vec2 q;
    q.x = fbm(uv.xy) + t.x;
    q.y = fbm(uv.yx) + t.y;

    t *= vec2(0.84, 0.66);

    vec2 r;
    r.x = fbm(uv.yx + q + t.x);
    r.y = fbm(uv.xy + q + t.y);

    t *= vec2(0.34, 0.54);

    return fbm(uv + r + t);
}

void main()
{
    vec2 UV = vs_pos.xy;
    UV.x *= u_aspect;

    // float x = truchet(UV, SCALE * 2.0);
    float x = stack_fbm(UV, SCALE);

    vec3 c0 = vec3(0.89, 0.77, 0.77);
    vec3 c1 = vec3(0.66, 0.23, 0.22);
    vec3 c2 = vec3(0.012, 0.003, 0.002);

    float r = x * 1.23;

    vec3 RGB;
    RGB = mix(c0, c1, max(r - 1.0, 0.0));
    RGB = mix(RGB, c2, max(r, 0.0));

    fs_color = vec4(RGB, 1.0);
}
