#version 460

in vec4 vs_pos;
in vec2 vs_uv;
in uint vs_id;

out vec4 fs_colour;

void main()
{
    vec2 uv = vs_uv.xy * 0.5 + 0.5;
    fs_colour = vec4(uv, 0.0, 1.0);
}
