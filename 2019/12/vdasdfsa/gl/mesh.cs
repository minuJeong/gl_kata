#version 460

layout(local_size_x=8, local_size_y=4) in;

struct Vertex
{
    vec4 in_pos;
    vec4 in_uv;
    vec4 in_color;
};

layout(binding=0) buffer vbo
{
    Vertex vertices[];
};

uniform float u_time;

const vec4 initial_pos[] = {
    vec4(-1.0, -1.0, 0.0, 1.0),
    vec4(+1.0, -1.0, 0.0, 1.0),
    vec4(-1.0, +1.0, 0.0, 1.0),
    vec4(+1.0, +1.0, 0.0, 1.0)
};

const vec4 initial_uv[] = {
    vec4(+0.0, +0.0, 0.0, 1.0),
    vec4(+1.0, +0.0, 0.0, 1.0),
    vec4(+0.0, +1.0, 0.0, 1.0),
    vec4(+1.0, +1.0, 0.0, 1.0)
};

float random(vec2 uv)
{
    highp float x = dot(uv, vec2(12.432143, 55.453215));
    x = mod(x, 3.14159284);
    return fract(sin(x) * 43215.453215);
}

void main()
{
    uint quad_id = gl_LocalInvocationID.x * gl_NumWorkGroups.x;
    uint vertex_id = gl_LocalInvocationID.y;

    uint dst_i = quad_id * 4 + vertex_id;
    uint src_i = uint(mod(dst_i, 4));

    vec4 pos = initial_pos[src_i];
    pos.xy *= 0.1;
    pos.x += float(quad_id) * 0.3 - 0.9;

    vertices[dst_i].in_pos = pos;

    vec4 uv = initial_uv[src_i];
    vertices[dst_i].in_uv = uv;

    vec3 RGB = vec3(0.1, 0.2, 0.3);
    vertices[dst_i].in_color = vec4(RGB, 1.0);

    if (vertex_id == 0)
    {
        vertices[dst_i].in_color.x = 1.0;
    }

    vertices[dst_i].in_color.w = 1.0;
}
