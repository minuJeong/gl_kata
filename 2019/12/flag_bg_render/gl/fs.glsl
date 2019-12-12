#version 460

#define SCALE 15.0
#define LINEWIDTH 0.07

layout(std430, binding=5) buffer constbuffer
{
    float u_time;
    float u_aspect;
};

in vec4 vs_pos;
out vec4 fs_color;


float random(vec2 uv)
{
    return fract(sin(dot(uv, vec2(12.4321, 46.76454))) * 43214.664321);
}

float truchet(vec2 uv, vec2 coord, float distfunc)
{
    float L = 0.5 - LINEWIDTH;
    float R = 0.5 + LINEWIDTH;
    float X;

    if (random(coord + vec2(0.0, 0.000004) * u_time) < 0.5)
    {
        uv.x = 1.0 - uv.x;
    }

    X = mix(uv.x + uv.y, length(uv), distfunc);
    float line_1 = X > L && X < R ? 1.0 : 0.0;

    uv = 1.0 - uv;
    X = mix(uv.x + uv.y, length(uv), distfunc);
    float line_2 = X > L && X < R ? 1.0 : 0.0;
    float line = max(line_1, line_2);
    return line;
}

float checkpattern(vec2 coord)
{
    return float(mod(coord.x, 2.0) == mod(coord.y, 2.0));
}

void main()
{
    vec2 uv = vs_pos.xy;
    uv.x *= u_aspect;
    uv = uv * 0.5 + 0.5;

    uv.x += 0.05 * u_time;

    uv *= SCALE;

    vec2 coord = floor(uv);
    vec2 local_uv = fract(uv);

    float T = cos(u_time * 0.65) * 0.5 + 0.5;

    float check = checkpattern(coord);
    float line = truchet(local_uv, coord, T);

    float x = max(line * 0.5, check * 0.15);

    x = clamp(x, 0.0, 1.0);
    fs_color = vec4(vec3(x), 1.0);
}
