#version 460

#define BLEND_PASS_THROUGH        0
#define BLEND_NORMAL              1
#define BLEND_DISSOLVE            2
#define BLEND_DARKEN              3
#define BLEND_MULTIPLY            4
#define BLEND_COLOR_BURN          5
#define BLEND_LINEAR_BURN         6
#define BLEND_DARKER_COLOR        7
#define BLEND_LIGHTEN             8
#define BLEND_SCREEN              9
#define BLEND_COLOR_DODGE         10
#define BLEND_LINEAR_DODGE        11
#define BLEND_LIGHTER_COLOR       12
#define BLEND_OVERLAY             13
#define BLEND_SOFT_LIGHT          14
#define BLEND_HARD_LIGHT          15
#define BLEND_VIVID_LIGHT         16
#define BLEND_LINEAR_LIGHT        17
#define BLEND_PIN_LIGHT           18
#define BLEND_HARD_MIX            19
#define BLEND_DIFFERENCE          20
#define BLEND_EXCLUSION           21
#define BLEND_SUBTRACT            22
#define BLEND_DIVIDE              23
#define BLEND_HUE                 24
#define BLEND_SATURATION          25
#define BLEND_COLOR               26
#define BLEND_LUMINOSITY          27

in vec4 vs_pos;
out vec4 fs_colour;

layout(binding=0) uniform sampler2D u_basecolour_tex;
uniform float u_time = 0.0;
uniform float u_tex_aspect = 1.0;
uniform int u_masktype = 0;
uniform float u_slider_alpha = 0.5;
uniform vec4 u_colour_picker = vec4(1.0, 1.0, 1.0, 1.0);
uniform int u_blendmode = 3;

float hash11(float x) { return fract(cos(x) * 43215.653421); }
float hash12(vec2 uv) { return hash11(dot(uv, vec2(12.4321454, 48.743216))); }
float hash13(vec3 pos) { return hash11(dot(pos, vec3(8.4321, 12.4321, 66.43216))); }

float noise12(vec2 uv)
{
    vec2 coord = floor(uv);
    float a = hash12(coord + vec2(0.0, 0.0));
    float b = hash12(coord + vec2(1.0, 0.0));
    float c = hash12(coord + vec2(0.0, 1.0));
    float d = hash12(coord + vec2(1.0, 1.0));

    vec2 fr = fract(uv);
    vec2 u = fr * fr * (3.0 - 2.0 * fr);

    float x0 = mix(a, b, u.x);
    float x1 = (c - a) * u.y * (1.0 - u.x);
    float x2 = (d - b) * u.x * u.y;
    return x0 + x1 + x2;
}

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

vec3 blend(vec3 src, vec3 dst, float alpha, uint mode)
{
    const vec3 LUM = vec3(0.2, 0.7, 0.1);
    const vec3 ONE = vec3(1.0);

    bool flag;
    vec3 above;
    vec3 below;
    vec3 hsv_src;
    vec3 hsv_dst;

    switch (mode)
    {
        case BLEND_PASS_THROUGH:
        return src;

        case BLEND_NORMAL:
        return mix(src, dst, alpha);

        case BLEND_DISSOLVE:
        return mix(src, alpha > 0.5 ? dst : src, alpha);

        case BLEND_DARKEN:
        return mix(src, min(src, dst), alpha);

        case BLEND_MULTIPLY:
        return mix(src, src * dst, alpha);

        case BLEND_COLOR_BURN:
        return mix(src, min(max(1.0 - (1.0 - src) / dst, 0.0), 1.0), alpha);

        case BLEND_LINEAR_BURN:
        return mix(src, dst + src - 1.0, alpha);

        case BLEND_LIGHTEN:
        return mix(src, max(src, dst), alpha);

        case BLEND_SCREEN:
        return mix(src, 1.0 - (1.0 - dst) * (1.0 - src), alpha);

        case BLEND_COLOR_DODGE:
        return mix(src, min(max(src / (1.0 - dst), 0.0), 1.0), alpha);

        // same as ADD
        case BLEND_LINEAR_DODGE:
        return mix(src, min(src + dst, 1.0), alpha);

        case BLEND_LIGHTER_COLOR:
        return mix(src, dot(src, LUM) > dot(dst, LUM) ? src : dst, alpha);

        case BLEND_OVERLAY:
        flag = dot(src, LUM) > 0.5;
        above = vec3(flag) * (1.0 - (1.0 - 2.0 * (src - 0.5)) * (1.0 - dst));
        below = vec3(!flag) * (2.0 * src) * dst;
        return mix(src, above + below, alpha);

        case BLEND_SOFT_LIGHT:
        flag = dot(dst, ONE) > 0.5;
        above = vec3(flag) * (1.0 - (1.0 - src) * (1.0 - (dst * 0.5)));
        below = vec3(!flag) * src * (dst + 0.5);
        return mix(src, above + below, alpha);

        case BLEND_HARD_LIGHT:
        flag = dot(dst, ONE) > 0.5;
        above = vec3(flag) * (1.0 - (1.0 - src) * (1.0 - 2.0 * (dst - 0.5)));
        below = vec3(!flag) * (src * (2.0 * dst));
        return mix(src, above + below, alpha);

        // [TODO] doesn't seem to work..
        case BLEND_VIVID_LIGHT:
        flag = dot(dst, ONE) > 0.5;
        above = vec3(flag) * (1.0 - (1.0 - src) / (2.0 * (dst - 0.5)));
        below = vec3(!flag) * (src / (1.0 - (2.0 * dst)));
        above + below;

        // debug color
        return mix(src, vec3(1.0, 0.0, 1.0), alpha);

        case BLEND_LINEAR_LIGHT:
        flag = dot(dst, ONE) > 0.5;
        above = vec3(flag) * (src + 2.0 * (dst - 0.5));
        below = vec3(!flag) * (src + 2.0 * dst - 1.0);
        return mix(src, above + below, alpha);

        case BLEND_PIN_LIGHT:
        flag = dot(dst, ONE) > 0.5;
        above = vec3(flag) * max(src, 2.0 * (dst - 0.5));
        below = vec3(!flag) * min(src, 2.0 * dst);
        return mix(src, above + below, alpha);

        // [TODO] couldn't figure out how it works in photoshop
        case BLEND_HARD_MIX:
        return mix(src, vec3(1.0, 0.0, 1.0), alpha);

        case BLEND_DIFFERENCE:
        return mix(src, abs(src - dst), alpha);

        case BLEND_EXCLUSION:
        return mix(src, 0.5 - 2.0 * (src - 0.5) * (dst - 0.5), alpha);

        case BLEND_SUBTRACT:
        return mix(src, max(src - dst, 0.0), alpha);

        case BLEND_DIVIDE:
        return mix(src, min(max(src / dst, 0.0), 1.0), alpha);

        case BLEND_HUE:
        hsv_src = rgb_to_hsv(src);
        hsv_dst = rgb_to_hsv(dst);
        hsv_src.x = hsv_dst.x;
        return mix(src, hsv_to_rgb(hsv_src), alpha);

        case BLEND_SATURATION:
        hsv_src = rgb_to_hsv(src);
        hsv_dst = rgb_to_hsv(dst);
        hsv_src.y = mix(hsv_src.y, hsv_dst.y, alpha);
        return hsv_to_rgb(hsv_src);

        case BLEND_COLOR:

        // debug color
        return mix(src, vec3(1.0, 0.0, 1.0), alpha);

        case BLEND_LUMINOSITY:
        hsv_src = rgb_to_hsv(src);
        hsv_dst = rgb_to_hsv(dst);
        hsv_src.z = mix(hsv_src.z, hsv_dst.z, alpha);
        return hsv_to_rgb(hsv_src);

        default :
        return src;
    }
    return src;
}

float truchet(vec2 uv, int style)
{
    float c = cos(u_time * 0.1), s = sin(u_time * 0.1), linewidth = 0.15, linespread = 0.002;
    vec2 coord;

    float L0 = 0.5 - linewidth, L1 = L0 + linespread, R0 = 0.5 + linewidth, R1 = R0 - linespread;
    
    vec2 mir_uv;
    switch(style)
    {
    case 0:
        linewidth = 0.21;
        L0 = 0.5 - linewidth, L1 = L0 + linespread, R0 = 0.5 + linewidth, R1 = R0 - linespread;

        uv.x += u_time * 0.1;
        uv *= 3.3;
        coord = floor(uv);
        uv -= coord;
        uv.x = hash12(coord) < 0.5 ? uv.x : 1.0 - uv.x;

        mir_uv = vec2(length(uv), length(1.0 - uv));
        break;

    case 1:
        linewidth = 0.2;
        L0 = 0.5 - linewidth, L1 = L0 + linespread, R0 = 0.5 + linewidth, R1 = R0 - linespread;

        uv.x -= u_time * 0.1;
        uv *= 4.7;
        coord = floor(uv);
        uv -= coord;
        uv.x = hash12(coord) < 0.5 ? uv.x : 1.0 - uv.x;

        mir_uv = vec2(uv.x + uv.y, (1.0 - uv).x + (1.0 - uv).y);
        break;

    case 2:
        linewidth = 0.075;
        L0 = 0.5 - linewidth, L1 = L0 + linespread, R0 = 0.5 + linewidth, R1 = R0 - linespread;

        uv = mat2(s, -c, c, s) * uv;
        uv *= 4.3;

        coord = floor(uv);
        uv -= coord;
        uv.x = hash12(coord) < 0.5 ? uv.x : 1.0 - uv.x;

        mir_uv = vec2(uv.x + uv.y, (1.0 - uv).x + (1.0 - uv).y);
        break;

    case 3:
        uv = mat2(c, -s, s, c) * uv;
        uv *= 2.3;

        coord = floor(uv);
        uv -= coord;
        uv.x = hash12(coord) < 0.5 ? uv.x : 1.0 - uv.x;

        mir_uv = vec2(length(uv), length(1.0 - uv));
        break;

    case 4:
        linewidth = 0.25;
        linespread = 0.002;
        L0 = 0.5 - linewidth, L1 = L0 + linespread, R0 = 0.5 + linewidth, R1 = R0 - linespread;

        uv *= 4.3;
        coord = floor(uv);
        uv -= coord;
        uv.x = hash12(coord) < cos(u_time * 4.2) * 0.5 + 0.5 ? uv.x : 1.0 - uv.x;

        mir_uv = vec2(uv.x + uv.y, (1.0 - uv).x + (1.0 - uv).y);
        break;
    }

    float truchet;
    truchet  = smoothstep(L0, L1, mir_uv.x) * smoothstep(R0, R1, mir_uv.x);
    truchet += smoothstep(L0, L1, mir_uv.y) * smoothstep(R0, R1, mir_uv.y);

    return truchet;
}

float fbm(vec2 uv)
{
    uv *= 2.2;
    uv.x += u_time * 0.13;
    uv.y += u_time * 0.06;
    float x = 0.0, a = 1.0, f = 2.0;
    for (int i = 0; i < 8; i++)
    {
        x += noise12(uv * f) * a;
        a *= 0.75;
        f *= 1.5;
    }
    return clamp(x * 0.5, 0.0, 1.0);
}

float stacked_fbm(vec2 uv, int style)
{
    float x, y, z, w;
    float c = cos(u_time * 0.05), s = sin(u_time * 0.05);

    switch(style)
    {

    // stack 2
    case 0:
        uv *= 0.25;
        x = fbm(uv);
        uv.x += x * 0.5;
        uv.y += u_time * 0.1;
        y = fbm(uv);
        return clamp(fbm(uv + vec2(y, x)), 0.0, 1.0);

    // stack 3
    case 1:
        uv *= 0.5;
        x = fbm(uv);
        uv.x += x * 2.5;
        y = fbm(uv);
        uv.x += cos(u_time * 0.1) * 0.6;
        uv.y += y * 0.2;
        z = fbm(uv);
        uv.x += z * cos(u_time * 0.5);
        uv.y += z * sin(u_time * 0.2);
        return clamp(fbm(uv.yx), 0.0, 1.0);

    // stack 4
    case 2:
        uv *= 0.3;
        x = fbm(uv);
        uv.x += x * 0.3 * cos(u_time * 0.01);
        uv.y += x;
        y = fbm(uv);
        uv.y += y * 0.2 * cos(u_time * 0.02);
        z = fbm(uv);
        uv.x += z * 0.2;
        w = fbm(uv);
        uv.x += w;
        return clamp(fbm(uv.xy), 0.0, 1.0);

    case 3:
        uv *= 0.25;
        x = fbm(uv);
        uv.x += x * -0.5;
        uv.y += sin(u_time * 0.2) * 0.2;
        y = fbm(uv);
        uv.x += y;
        uv.y += x + y;
        return clamp(fbm(uv), 0.0, 1.0);
    }
    return fbm(uv);
}

float checker_pattern(vec2 uv)
{
    uv *= 4.0;
    vec2 coord = floor(uv);
    if (abs(mod(coord.x, 2.0) - mod(coord.y, 2.0)) < 0.1)
    {
        return 0.0;
    }
    return 1.0;
}

void main()
{
    vec2 tuv, uv = vs_pos.xy;
    tuv = uv * 0.5 + 0.5;

    tuv.x /= u_tex_aspect;
    tuv.y = 1.0 - tuv.y;

    float alpha = 1.0;

    float mask = 0.0;
    switch(u_masktype)
    {

    // truchet
    case 0:
    case 1:
    case 2:
    case 3:
    case 4:
        mask = truchet(uv, u_masktype);
        break;

    // cloudy noise
    case 5:
        mask = fbm(uv * 1.5 + vec2(u_time * 0.15, 0.0));
        break;
    case 6:
    case 7:
    case 8:
    case 9:
        mask = stacked_fbm(uv, u_masktype - 6);
        break;

    // flat full
    case 10:
        mask = 1.0;
        break;

    // flat none
    case 11:
        mask = 0.0;
        break;

    // checker
    case 12:
        mask = checker_pattern(uv);
        break;

    default:
        mask = 0.0;
        break;
    }

    vec3 overlay = u_colour_picker.xyz;
    vec3 tex_rgb = texture(u_basecolour_tex, tuv).xyz;

    int blend_mode = -1;
    switch(u_blendmode)
    {
    case 0:
    blend_mode = BLEND_NORMAL;
    break;
    case 1:
    blend_mode = BLEND_MULTIPLY;
    break;
    case 2:
    blend_mode = BLEND_OVERLAY;
    break;
    case 3:
    blend_mode = BLEND_HUE;
    break;
    case 4:
    blend_mode = BLEND_SOFT_LIGHT;
    break;
    }

    vec3 rgb = blend(tex_rgb, overlay, mask * u_slider_alpha, blend_mode);
    vec3 rgb2 = blend(tex_rgb, overlay, mask * u_slider_alpha, BLEND_MULTIPLY);
    rgb = mix(rgb, rgb2, 0.5);

    fs_colour = vec4(rgb, alpha);
}
