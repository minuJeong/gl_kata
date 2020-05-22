#version 460

in GSOUT
{
    vec4 pos;
} gs_out;
out vec4 fs_color;

uniform float u_time;
uniform vec3 u_camera_pos;

void main()
{
    vec3 pos = gs_out.pos.xyz;
    vec2 uv = pos.xz;
    vec3 rgb = vec3(0.0);

    uv = uv * 0.5;

    uv *= 10.0;
    vec2 xy = floor(uv);
    uv = fract(uv + 0.5);

    rgb.xy = uv;
    rgb.z = pos.y * 23.0;

    fs_color = vec4(rgb, 1.0);
}
