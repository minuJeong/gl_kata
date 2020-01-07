#version 460

struct CONST
{
    vec4 u_campos;
};

layout(binding=0) buffer constbuffer
{
    CONST constants;
};

in vec3 vs_pos;

out vec4 fs_color;

void main()
{
    vec2 uv = vs_pos.xy * 0.5 + 0.5;
    vec3 RGB = vec3(uv, 0.5);

    RGB = constants.u_campos.xyz;

    RGB = abs(RGB);
    fs_color = vec4(RGB, 1.0);
}
