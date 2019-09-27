#version 460

#define saturate(x) min(max(x, 0.0), 1.0)

struct VoronoiDot
{
    vec2 pos;
    float _leftover;
    float col;
};

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer bind_0
{
    vec4 data_0[];
};

layout(binding=1) buffer bind_1
{
    VoronoiDot data_1[];
};

uniform uint u_width;
uniform uint u_height;
uniform float u_time;

uniform uint u_numdots;


float random (vec2 st)
{ return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123); }

VoronoiDot pick_closest(vec2 uv)
{
    VoronoiDot closest = data_1[0];
    for (int i = 0; i < u_numdots; i++)
    {
        VoronoiDot d = data_1[i];
        vec2 dx = uv - closest.pos;
        vec2 dy = uv - d.pos;
        if (dot(dx, dx) > dot(dy, dy))
        {
            closest = d;
        }
    }
    return closest;
}

void main()
{
    uvec2 wh = uvec2(u_width, u_height);
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * 8;
    uint i = xy.x + xy.y * u_width;

    vec2 uv = vec2(xy) / vec2(wh);

    VoronoiDot dot = pick_closest(uv);
    vec3 rgb = vec3(random(vec2(cos(dot.col), sin(dot.col))),
                    random(vec2(sin(dot.col), cos(dot.col))),
                    random(vec2(cos(dot.col), cos(dot.col))));

    data_0[i] = vec4(rgb, 1.0);
}
