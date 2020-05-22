#version 460

in vec4 vs_position;
out vec4 fs_colour;

uniform float u_time;

layout(binding=0) uniform sampler2D u_texture;

float hash12(vec2 uv) { return fract(cos(dot(uv, vec2(12.43215, 43.513243))) * 43215.432143); }

void main()
{
    vec2 uv = vs_position.xy;

    uv *= 4.0;
    vec2 coord = floor(uv);
    uv = fract(uv);

    float random = hash12(coord) * 2.0;
    float c = cos(random), s = sin(random);
    uv = mat2(c, -s, s, c) * uv;

    vec4 texture_data = texture(u_texture, uv);

    fs_colour = vec4(texture_data.xyz, 1.0);
}
