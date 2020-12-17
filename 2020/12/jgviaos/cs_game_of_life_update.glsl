#version 460
#define BUFFER_WIDTH 64
#define RENDER_WIDTH 1024

layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer b0
{
    bool is_alive_from[];
};

layout(binding=1) buffer b1
{
    bool is_alive_to[];
};

uint get_i(uvec2 xy) { return xy.x + xy.y * BUFFER_WIDTH; }
uint get_i(uint x, uint y) { return get_i(uvec2(x, y)); }

uint count_neighbors(uint x, uint y)
{
    uint sum = 0;
    sum += is_alive_from[get_i(x - 1, y - 1)] ? 1 : 0;
    sum += is_alive_from[get_i(x + 0, y - 1)] ? 1 : 0;
    sum += is_alive_from[get_i(x + 1, y - 1)] ? 1 : 0;
    sum += is_alive_from[get_i(x - 0, y + 0)] ? 1 : 0;
    sum += is_alive_from[get_i(x + 1, y + 0)] ? 1 : 0;
    sum += is_alive_from[get_i(x - 1, y + 1)] ? 1 : 0;
    sum += is_alive_from[get_i(x + 0, y + 1)] ? 1 : 0;
    sum += is_alive_from[get_i(x + 1, y + 1)] ? 1 : 0;
    return sum;
}

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;

    bool is_alive = is_alive_from[get_i(xy)];
    uint neighbors = count_neighbors(xy.x, xy.y);

    if (is_alive)
    {
        is_alive = neighbors == 2 || neighbors == 3 ? true : false;
    }
    else
    {
        is_alive = neighbors == 3 ? true : false;
    }

    is_alive_to[get_i(xy)] = is_alive;
}
