#version 460

in vec4 vs_pos;
out vec4 fs_color;

void main()
{
    vec3 pos = vs_pos.xyz;

    float dx = abs(dot(pos, vec3(1.0, 0.0, 0.0)));
    float dy = abs(dot(pos, vec3(0.0, 1.0, 0.0)));
    float dz = abs(dot(pos, vec3(0.0, 0.0, 1.0)));
    vec2 uv = pos.yz * dx + pos.xz * dy + pos.xy * dz;
    uv = mod(uv, 1.0);

    fs_color = vec4(uv, 0.4, 1.0);
}
