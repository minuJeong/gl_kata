#version 460

in vec4 vs_pos;
out vec4 fs_color;

uniform sampler2D u_tex_0;
uniform vec2 u_tex_0_resolution;
uniform vec2 u_resolution;

void main()
{
    vec2 uv = vs_pos.xy;
    uv.x /= u_resolution.y / u_resolution.x;
    uv.x *= u_tex_0_resolution.y / u_tex_0_resolution.x;
    uv = uv * 0.5 + 0.5;
    uv = 1.0 - uv;

    vec4 tex = texture(u_tex_0, uv);

    fs_color = vec4(tex.zyx, 1.0);
}