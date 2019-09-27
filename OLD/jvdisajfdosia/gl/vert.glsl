#version 460

in vec3 in_pos;

out vec2 vtx_uv;

void main()
{
    vtx_uv = in_pos.xy * 0.5 + 0.5;
    gl_Position = vec4(in_pos, 1.0);
}
