#version 460

uniform float u_time;

in vec2 vtx_uv;
out vec4 out_color;

void main()
{
    float blue = cos(u_time * 0.2) * 0.5 + 0.5;

    vec3 rgb = vec3(vtx_uv, blue);
    out_color = vec4(rgb, 1.0);
}
