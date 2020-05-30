#version 460

in struct VS_OUT
{
    vec4 pos;
} vs_out;
out vec4 fs_color;

void main()
{
    vec2 uv = vs_out.pos.xy;
    fs_color = vec4(uv, 0.0, 1.0);
}
