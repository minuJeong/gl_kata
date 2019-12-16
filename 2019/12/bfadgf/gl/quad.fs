#version 460

in vec4 vs_pos;
out vec4 fs_color;

struct Const
{
    float u_aspect;
    float u_time;
};

const float HALF = 0.5;
const float WIDTH = 0.25;

float random(vec2 uv)
{
    highp float x = dot(uv, vec2(12.4321, 55.43215));
    highp float y = mod(x, 3.1415928);
    highp float z = cos(y) * 43125.53214321;
    return fract(z);
}

layout(binding=14) buffer constbuffer
{
    Const b_const;
};

void main()
{
    vec2 uv = vs_pos.xy;

    uv = uv * 7.0;
    vec2 coord = floor(uv);
    uv = fract(uv);

    float x, y;
    x = random(coord);
    uv.x = x < 0.5 ? uv.x : 1.0 - uv.x;

    x = uv.x + uv.y;
    x = smoothstep(HALF - WIDTH, HALF - WIDTH + 0.01, x) * smoothstep(HALF + WIDTH, HALF + WIDTH - 0.01, x);

    uv = 1.0 - uv;
    y = uv.x + uv.y;
    y = smoothstep(HALF - WIDTH, HALF - WIDTH + 0.01, y) * smoothstep(HALF + WIDTH, HALF + WIDTH - 0.01, y);

    x = max(x, y);

    fs_color = vec4(x, x, x, 1.0);
}
