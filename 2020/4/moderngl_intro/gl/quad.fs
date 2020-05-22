#version 460

in vec4 vs_position;
out vec4 fs_colour;

uniform vec2 u_resolution;
layout(binding=0) uniform sampler2D u_texture;

float hash12(vec2 coord)
{
    return cos(dot(coord, vec2(12.43214, 43.43215))) * 43214.523115;
}

void main()
{
    vec2 uv = vs_position.xy;
    uv *= 4.0;

    vec2 coord = floor(uv);
    uv = fract(uv);

    float random = hash12(coord);
    float c = cos(random), s = sin(random);
    uv = mat2(c, -s, s, c) * uv;

    vec4 tex_data = texture(u_texture, uv);
    vec3 rgb = tex_data.xyz;

    fs_colour = vec4(rgb, 1.0);
}
