#version 460

layout(binding=0) buffer bind_0
{
    vec4 data_0[];
};

layout(binding=1) buffer bind_1
{
    vec4 data_1[];
};

in vec2 v_uv;

out vec4 out_col;

uniform uint u_width;
uniform uint u_height;
uniform float u_time;

void main()
{
    vec2 wh = vec2(u_width, u_height);
    uvec2 xy = uvec2(v_uv * wh);
    uint i = xy.x + xy.y * u_width;

    vec4 col = vec4(0.0);

    float c = cos(u_time * 12.0);

    vec4 a = data_0[i];
    vec4 b = data_1[i];

    col.xyz = (a.xyz + b.xyz) * 0.5;

    out_col.xyz = col.xyz;
}
