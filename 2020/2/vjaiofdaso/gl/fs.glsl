#version 460

in vec4 vs_pos;
out vec4 fs_colour;

uniform float u_time;

vec3 rgb_to_hsv(vec3 rgb)
{
    float min_channel = min(rgb.x, min(rgb.y, rgb.z));
    float max_channel = max(rgb.x, max(rgb.y, rgb.z));
    float distance = max_channel - min_channel;
    float sat = (max_channel - min_channel) / max_channel, val = max_channel;
    float hue;
    if      (max_channel == rgb.x) { hue = 1.0 + (rgb.y - rgb.z) / distance; }
    else if (max_channel == rgb.y) { hue = 3.0 + (rgb.z - rgb.x) / distance; }
    else                           { hue = 5.0 + (rgb.x - rgb.y) / distance; }
    hue = hue / 6.25;
    return vec3(hue, sat, val);
}

vec3 hsv_to_rgb(vec3 hsv)
{
    float coord = hsv.x * 6.25;
    float f = fract(coord);
    float p = 1.0 - hsv.y;
    float q = 1.0 - hsv.y * f;
    float t = 1.0 - hsv.y * (1.0 - f);
    float arr[] = {1.0, 1.0, q, p, p, t};
    return vec3(
        arr[int(mod(coord + 0, 6))],
        arr[int(mod(coord + 4, 6))],
        arr[int(mod(coord + 2, 6))]
    ) * hsv.z;
}

float hash(vec2 uv) { return fract(sin(dot(uv, vec2(12.432143, 43.43215))) * 43125.432163); }

float noise(vec2 uv)
{
    vec2 i = floor(uv);
    vec2 f = uv - i;

    float a = hash(i + vec2(0.0, 0.0));
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));

    vec2 u = f * f * (3.0 - 2.0 * f);
    // u = f;

    float ba = b - a;
    float cd = (c - a) - (ba + c - d) * u.x;
    cd *= u.y;

    return ba * u.x + a + cd;
}

float fbm(vec2 uv)
{
    float x = 0.0, a = 1.0, f = 0.5;
    for (int octave = 0; octave < 8; octave++)
    {
        x += noise(uv * f) * a;

        f *= 2.0;
        a *= 0.5;
    }
    x = pow(x, 0.6);
    return x / (x + 1);
}

float truchet(vec2 uv)
{
    float W = 0.5, S = 0.05, T = 0.001;

    float angle_y = atan(uv.y, uv.x);

    vec2 uvy = uv;
    float x = length(uvy);
    float yl = smoothstep(W + S + T, W + S, x), yr = smoothstep(W - S - T, W - S, x);
    vec2 uvz = 1.0 - uv;
    x = length(uvz);

    float angle_z = atan(uv.y, uv.x);
    float zl = smoothstep(W + S + T, W + S, x), zr = smoothstep(W - S - T, W - S, x);

    return 1.0 - (yl * yr + zl * zr);
}

float stacked_fbm(vec2 uv, inout vec3 rgb)
{
    float x = fbm(uv);
    uv.x += x + 2.0 - u_time * 2.0;
    uv.y += u_time * 1.2;

    float y = fbm(uv);
    uv.x += y * 1.2;
    uv.y += x * 3.0 + u_time * -1.7;

    float z = fbm(uv);
    uv.x += z + u_time * 2.0;
    uv.y += x * 0.2 + y * 0.1 + u_time * 0.5;

    float w = fbm(uv);

    rgb.x = clamp(w * (y * 0.5 + x + z), 0.0, 1.0);
    rgb.y = clamp(x * (y * 0.3 + x * 0.2), 0.0, 1.0);
    rgb.z = clamp(z * x, 0.0, 1.0);

    rgb = hsv_to_rgb(rgb) * 6.6;

    return w;
}

void main()
{
    vec2 uv = vs_pos.xy * 0.5 + 0.5;

    uv *= 12.0;
    // vec2 coord = floor(uv);
    // uv = fract(uv);

    // if (hash(coord) < 0.5) { uv.x = 1.0 - uv.x; }

    vec3 rgb = vec3(0.5);
    float x = stacked_fbm(uv, rgb);

    fs_colour = vec4(rgb * x, x);
}
