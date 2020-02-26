#version 460

in vec4 vs_pos;
out vec4 fs_colour;

void main()
{
    vec2 uv;
    vec3 rgb;
    float alpha;
    uv = vs_pos.xy;
    uv *= 5.0;
    vec2 coord = floor(uv);
    uv = fract(uv);

    

    alpha = 1.0;
    fs_colour = vec4(rgb * alpha, alpha);
}
