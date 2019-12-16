#version 460

layout(local_size_x=8, local_size_y=8) in;

layout(binding=1) buffer b_screen_draw
{
    vec4 b_draw_rgb[];
};

uniform uvec2 u_res = uvec2(512, 512);
uniform bool u_is_draw;
uniform bool u_is_erase;
uniform vec2 u_prevmousepos;
uniform vec2 u_mousepos;

float sdf2d_line(vec2 p, vec2 a, vec2 b)
{
    vec2 pa = p - a;
    vec2 ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h);
}

uint buf_pos_at(uvec2 xy)
{
    return xy.x + xy.y * u_res.x;
}

uint buf_pos_at(vec2 pos)
{
    return buf_pos_at(uvec2(pos + 0.5));
}

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;
    uint i = buf_pos_at(xy);
    vec3 RGB = b_draw_rgb[i].xyz;

    if (u_is_draw)
    {
        float dist = sdf2d_line(xy, u_mousepos, u_prevmousepos);
        RGB.x += smoothstep(8.1, 8.0, dist);
        RGB.z = 0.5;
    }
    else
    {
        RGB.z = 0.0;
    }

    if (u_is_erase)
    {
        RGB.xyz = vec3(0.0);
    }

    if (xy.x < 32 || xy.y < 32 ||
        xy.x > 512 - 32 || xy.y > 512 - 32)
    {
        RGB.x = 0.1;
    }

    RGB = clamp(RGB, 0.0, 1.0);
    b_draw_rgb[i] = vec4(RGB, 1.0);
}
