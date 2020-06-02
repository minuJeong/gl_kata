#version 460

in struct GS_OUT
{
    vec4 position;
    vec2 texcoord0;
    vec2 texcoord1;
    float rand;
} gs_out;
out vec4 fs_color;

void main()
{
    vec2 uv = gs_out.texcoord0.xy * 0.5 + 0.5;
    vec3 rgb = vec3(0.0);

    rgb.xy = uv;
    rgb.z = gs_out.rand;

    fs_color = vec4(rgb, 1.0);
}
