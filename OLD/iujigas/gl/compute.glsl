#version 460

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer bind_0
{
    vec4 data_0[];
};

layout(binding=1) buffer bind_1
{
    vec4 data_1[];
};

uniform float u_time;
uniform uint u_width;
uniform uint u_height;


void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * 8;
    uint i = xy.x + xy.y * u_width;

    vec2 wh = vec2(u_width, u_height);
    vec2 uv = vec2(xy) / wh;

    uv = uv * 2.0 - 1.0;
    float d = length(uv);

    float c = cos(d * 12.0 + (u_time * 15.0));
    float s = sin(d * 12.0 + (u_time * 15.0));
    uv = mat2(c, -s, s, c) * uv;

    vec3 rgb = vec3(0.0);
    rgb.xy = abs(uv.xy);
    rgb.z = 0.5;

    data_0[i] = vec4(rgb.xyz, 1.0);
    data_1[i] = vec4(rgb.zyx, 1.0);
}
