#version 460
layout(local_size_x=8, local_size_y=8) in;

struct Cell
{
    vec4 is_alive;
};

layout(binding=0) buffer buffer_0
{
    Cell cell_from[];
};

layout(binding=1) buffer buffer_1
{
    Cell cell_to[];
};

uniform float u_time;
uniform uvec2 u_resolution;

uint xy_to_i(uvec2 xy) { return xy.x + xy.y * u_resolution.x; }

int count_living_neighbors(uvec2 xy)
{
    int sum = 0;

    sum += cell_from[xy_to_i(xy + uvec2(-1, -1))].is_alive.x == 1.0 ? 1 : 0;
    sum += cell_from[xy_to_i(xy + uvec2(+0, -1))].is_alive.x == 1.0 ? 1 : 0;
    sum += cell_from[xy_to_i(xy + uvec2(+1, -1))].is_alive.x == 1.0 ? 1 : 0;

    sum += cell_from[xy_to_i(xy + uvec2(-1, +0))].is_alive.x == 1.0 ? 1 : 0;
    sum += cell_from[xy_to_i(xy + uvec2(+1, +0))].is_alive.x == 1.0 ? 1 : 0;

    sum += cell_from[xy_to_i(xy + uvec2(-1, -1))].is_alive.x == 1.0 ? 1 : 0;
    sum += cell_from[xy_to_i(xy + uvec2(+0, -1))].is_alive.x == 1.0 ? 1 : 0;
    sum += cell_from[xy_to_i(xy + uvec2(+1, -1))].is_alive.x == 1.0 ? 1 : 0;

    return sum;
}

bool check_is_alive(uvec2 xy)
{
    uint i = xy_to_i(xy);

    float me = cell_from[i].is_alive.x;
    int c = count_living_neighbors(xy);

    return (me == 1 && 1 > c && c < 4) || (me == 0 && c == 3);
}

void main()
{
    uvec2 xy = gl_LocalInvocationID.xy + gl_WorkGroupID.xy * gl_WorkGroupSize.xy;
    uint i = xy_to_i(xy);

    vec2 uv = vec2(xy) / vec2(u_resolution.xy);

    Cell cell = cell_from[i];

    int c = count_living_neighbors(xy);

    cell.is_alive = vec4(check_is_alive(xy) ? 1 : 0, 0.0, 0.0, 1.0);

    cell_to[i] = cell;
}
