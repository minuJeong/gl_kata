#version 460

in vec2 vs_pos;
out vec4 fs_color;

layout(location=2) uniform sampler2D u_source;

uniform bool u_is_hor = false;
uniform vec2 u_res = vec2(1, 1);

const float weight[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);


void main()
{
    vec2 uv = vs_pos * 0.5 + 0.5;
    vec2 offset = 1.0 / u_res;
    vec3 RGB = texture(u_source, uv).xyz;

    vec2 texoffset = u_is_hor ? vec2(offset.x, 0.0) : vec2(0.0, offset.y);
    for (int i = 0; i < 5; i++)
    {
        RGB += texture(u_source, uv + texoffset * i).xyz * weight[i];
        RGB += texture(u_source, uv - texoffset * i).xyz * weight[i];
    }

    RGB.x = offset.y * 1280.0 * 0.5;
    fs_color = vec4(RGB, 1.0);
}
