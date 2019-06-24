#version 460
#define saturate(x) min(max(x, 0.0), 1.0)

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer bind_0
{
    vec4 data_0[];
};

uniform uint u_width;
uniform uint u_height;


void main()
{
    float aspect = float(u_width) / float(u_height);
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * 8;
    uint i = xy.x + xy.y * u_width;

    uvec2 wh = uvec2(u_width, u_height);
    vec2 uv = vec2(vec2(xy) / vec2(wh));

    vec2 ruv = uv * 2.0 - 1.0;
    ruv.x *= aspect;

    float d = length(ruv);

    float c = cos(d * 12.0);
    float s = sin(d * 12.0);
    ruv.xy = mat2(c, -s, s, c) * ruv.xy;

    ruv *= 2.0;
    ruv = mod(ruv, vec2(1.0));

    vec3 rgb = vec3(saturate(ruv), 0.5);

    data_0[i] = vec4(rgb, 1.0);
}
