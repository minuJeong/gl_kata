#version 460

in vec4 vs_pos;
out vec4 fs_color;

uniform int u_idx;
uniform vec3 u_color;


float random(float x)
{
    return fract(sin(x * x) * 54314.432153);
}

float lum(vec3 col)
{
    return dot(vec3(0.2, 0.7, 0.1), col);
}

void main()
{
    float r = random(float(u_idx));

    vec3 RGB = lum(u_color) < 0.5 ? vec3(0.5) : u_color;

    fs_color = vec4(RGB, 1.0);
}
