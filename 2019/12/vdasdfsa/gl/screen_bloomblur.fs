#version 460

in vec2 vs_pos;
out vec4 fs_color;

layout(location=0) uniform sampler2D u_source;

uniform vec2 u_res = vec2(1, 1);

const float weight[5] = float[] (
    0.93, 0.66, 0.44, 0.25, 0.07
);

void main()
{
    vec2 uv = vs_pos * 0.5 + 0.5;
    vec2 offset = 5.0 / u_res;

    vec3 RGB = texture(u_source, uv).xyz;

    if (dot(RGB, vec3(0.2, 0.7, 0.1)) < 1.0)
    {
        fs_color = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    for (int x = -5; x < 6; x++)
    for (int y = -5; y < 6; y++)
    {
        int i = max(abs(x), abs(y));
        vec3 left = texture(u_source, uv + vec2(offset.x * x, offset.y * y)).xyz * weight[i];
        vec3 right = texture(u_source, uv - vec2(offset.x * x, offset.y * y)).xyz * weight[i];
        RGB += left + right;
    }

    fs_color = vec4(RGB, 1.0);
}
