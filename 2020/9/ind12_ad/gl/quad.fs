#version 460

in vec4 vs_pos;
out vec4 fs_color;

uniform float u_time;

float hash(vec2 pos)
{
    float x = dot(pos, vec2(12.37862, 45.75464));
    return fract(cos(x) * 44531.86532);
}

void main()
{
    vec2 uv = vs_pos.xy;

    vec3 ray = normalize(vec3(uv, 1.0));

    vec3 rgb = vec3(0.3, 0.3, 0.3);
    fs_color = vec4(rgb, 1.0);
}
