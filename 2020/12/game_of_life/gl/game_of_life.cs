#version 460

layout(local_size_x=8, local_size_y=8) in;

struct Cell
{
    ivec4 is_alive;
    vec4 color;
};

layout(binding=0) buffer cells_buffer_from
{
    Cell cells_from[];
};

layout(binding=1) buffer cells_buffer_to
{
    Cell cells_to[];
};

uniform int u_map_size = 256;
uniform ivec2 u_pos;
uniform int u_is_drag;
uniform float u_time;

float hash(vec2 uv)
{
    float x = dot(uv, vec2(12.321, 45.321));
    return fract(cos(x) * 43216.1);
}

int xy2i(int x, int y)
{
    x = min(max(x, 0), u_map_size - 1);
    y = min(max(y, 0), u_map_size - 1);
    return x + y * u_map_size;
}
int xy2i(uint x, uint y) { return xy2i(int(x), int(y)); }

int count_surrounding_lives(int x, int y)
{
    int lives = 0;
    lives += cells_from[xy2i(x - 1, y + 1)].is_alive.x == 1 ? 1 : 0;
    lives += cells_from[xy2i(x + 0, y + 1)].is_alive.x == 1 ? 1 : 0;
    lives += cells_from[xy2i(x + 1, y + 1)].is_alive.x == 1 ? 1 : 0;

    lives += cells_from[xy2i(x - 1, y + 0)].is_alive.x == 1 ? 1 : 0;
    lives += cells_from[xy2i(x + 1, y + 0)].is_alive.x == 1 ? 1 : 0;

    lives += cells_from[xy2i(x - 1, y - 1)].is_alive.x == 1 ? 1 : 0;
    lives += cells_from[xy2i(x + 0, y - 1)].is_alive.x == 1 ? 1 : 0;
    lives += cells_from[xy2i(x + 1, y - 1)].is_alive.x == 1 ? 1 : 0;
    return lives;
}

void main()
{
    int x = int(gl_LocalInvocationID.x + gl_WorkGroupID.x * gl_WorkGroupSize.x);
    int y = int(gl_LocalInvocationID.y + gl_WorkGroupID.y * gl_WorkGroupSize.y);
    Cell self = cells_from[xy2i(x, y)];
    int is_alive = self.is_alive.x;
    float alive_time = self.color.x;

    if (u_is_drag == 1)
    {
        vec2 uv = vec2(x, y) / u_map_size;

        float dist = length(vec2(x, y) - u_pos);
        is_alive = is_alive == 1 || dist < 32 && hash(uv + u_time) < 0.05 ? 1 : 0;
    }
    else
    {
        int sur = count_surrounding_lives(x, y);
        if (self.is_alive == 0)
        {
            is_alive = sur == 3 ? 1 : 0;
            alive_time = sur == 3 ? min(alive_time + 0.1, 1.0) : 0.0;
        }
        else
        {
            is_alive = sur == 2 || sur == 3 ? 1 : 0;
            alive_time -= 0.02;
        }
    }

    vec2 uv = vec2(x, y) / u_map_size;
    uv.xy = vec2(gl_WorkGroupID.xy) / 16.0;

    vec3 rgb = vec3(alive_time, 0.2, 0.8);
    float alpha = 1.0;

    Cell to = cells_to[xy2i(x, y)];
    to.is_alive = ivec4(is_alive, 0, 0, 0);
    to.color = vec4(rgb, alpha);

    cells_to[xy2i(x, y)] = to;
}
