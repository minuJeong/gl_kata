#version 460

in vec2 vs_pos;
out vec4 fs_color;


float box2d(vec2 p, vec2 b)
{
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

void main()
{
    vec2 pos = vs_pos;
    vec2 uv = pos * 0.5 + 0.5;

    float d = box2d(pos, vec2(0.5)) - 0.15;
    d = d <= 0.0 ? 1.0 : 0.0;

    vec3 RGB;
    RGB.x = 1.0;
    fs_color = vec4(RGB, d);
}
