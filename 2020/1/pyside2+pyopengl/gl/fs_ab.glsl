#version 460

in vec4 vs_pos;
out vec4 fs_color;

void main()
{
    vec2 uv = vs_pos.xy;
    uv = uv * 0.5 + 0.5;
    float depth = gl_FragCoord.z * 0.5;

    vec3 RGB = vec3(uv, depth);
    fs_color = vec4(RGB, 1.0);
}
