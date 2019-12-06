#version 460

in GS_OUT
{
    vec4 position;
    vec4 velocity;
    vec4 color;
    vec4 texcoord;
} gs_out;

out vec4 fs_color;

void main()
{
    fs_color.xy = gs_out.color.xy;
    fs_color.z = 0.3;
    fs_color.w = 1.0;
}
