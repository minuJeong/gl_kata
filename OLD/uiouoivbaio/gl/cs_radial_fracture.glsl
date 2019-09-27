#version 460


layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer bind_0
{
    vec4 data_0[];
};

uniform uint u_width;
uniform uint u_height;


void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * 8;
    uvec2 wh = uvec2(u_width, u_height);
    vec2 uv = vec2(xy / vec2(wh));

    vec3 rgb = vec3(uv, 0.0);

    uint i = xy.x + xy.y * u_width;
    data_0[i] = vec4(rgb, 1.0);
}
