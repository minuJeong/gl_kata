#version 460

in vec4 vs_pos;
out vec4 fs_color;

layout(location=0) uniform sampler2D u_gb_color;

void main()
{
    vec2 uv = vs_pos.xy * 0.5 + 0.5;
    vec4 tex_col = texture(u_gb_color, uv);
    fs_color = vec4(tex_col.xyz, 1.0);
}
