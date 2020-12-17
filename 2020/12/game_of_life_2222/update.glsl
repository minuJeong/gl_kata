#version 460
#define WIDTH 128
#define RENDERWIDTH 512

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer b0
{
    bool is_live_from[];
};

layout(binding=1) buffer b1
{
    bool is_live_to[];
};

uint xy_to_i(ivec2 xy)
{
    xy.x = min(max(xy.x, 0), WIDTH - 1);
    xy.y = min(max(xy.y, 0), WIDTH - 1);
    return xy.x + xy.y * WIDTH;
}

int count_living_neighbors(ivec2 xy)
{
    int sum = 0;
    sum += is_live_from[xy_to_i(xy + ivec2(-1, -1))] ? 1 : 0;
    sum += is_live_from[xy_to_i(xy + ivec2(+0, -1))] ? 1 : 0;
    sum += is_live_from[xy_to_i(xy + ivec2(+1, -1))] ? 1 : 0;
    sum += is_live_from[xy_to_i(xy + ivec2(-1, +1))] ? 1 : 0;
    sum += is_live_from[xy_to_i(xy + ivec2(+0, +1))] ? 1 : 0;
    sum += is_live_from[xy_to_i(xy + ivec2(+1, +1))] ? 1 : 0;
    sum += is_live_from[xy_to_i(xy + ivec2(-1, +0))] ? 1 : 0;
    sum += is_live_from[xy_to_i(xy + ivec2(+1, +0))] ? 1 : 0;

    return sum;
}

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;
    uint i = xy.x + xy.y * WIDTH;

    bool is_alive = is_live_from[i];
    int count = count_living_neighbors(ivec2(xy));

    if (is_alive)
    {
        is_alive = count == 3 || count == 4;
    }
    else
    {
        is_alive = count == 3;
    }

    is_live_to[i] = is_alive;
}
