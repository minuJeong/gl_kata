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
uniform float u_slider_alpha = 0.0;
uniform float u_slider_hue = 0.0;

float hash11(float x) { return fract(sin(x) * 43215.653421); }
float hash12(vec2 uv) { return hash11(dot(uv, vec2(12.4321, 66.43216))); }
float hash13(vec3 pos) { return hash11(dot(pos, vec3(8.4321, 12.4321, 66.43216))); }

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
        hsv_src.x = mix(hsv_src.x, hsv_dst.x, alpha);
        return hsv_to_rgb(hsv_src);

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


void main()
{
    vec2 tuv, uv = vs_pos.xy, coord, mir_uv;
    tuv = uv * 0.5 + 0.5;
    uv.x += u_time * 0.3;

    tuv.x /= u_tex_aspect;
    tuv.y = 1.0 - tuv.y;

    float alpha = 1.0, linewidth = 0.15, linespread = 0.1, truchet;

    uv *= 2.3;
    coord = floor(uv);
    uv -= coord;
    uv.x = hash12(coord) < 0.5 ? uv.x : 1.0 - uv.x;

    float L0 = 0.5 - linewidth, L1 = L0 + linespread, R0 = 0.5 + linewidth, R1 = R0 - linespread;
    // mir_uv = vec2(uv.x + uv.y, (1.0 - uv).x + (1.0 - uv).y);
    mir_uv = vec2(length(uv), length(1.0 - uv));
    truchet  = smoothstep(L0, L1, mir_uv.x) * smoothstep(R0, R1, mir_uv.x);
    truchet += smoothstep(L0, L1, mir_uv.y) * smoothstep(R0, R1, mir_uv.y);

    vec3 overlay = hsv_to_rgb(vec3(u_slider_hue, 1.0, 1.0));

    vec3 tex_rgb = texture(u_basecolour_tex, tuv).xyz;
    vec3 hue_blended = blend(tex_rgb, overlay, truchet, BLEND_HUE);
    vec3 rgb = mix(tex_rgb, hue_blended, u_slider_alpha);

    fs_colour = vec4(rgb, alpha);
}
