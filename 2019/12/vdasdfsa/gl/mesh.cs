#version 460

layout(local_size_x=8, local_size_y=4) in;

struct Particle
{
    vec4 in_pos;
    vec4 in_uv;
    vec4 in_color;
};

layout(binding=0) buffer vbo
{
    Particle vertices[];
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
    uint num_quads = gl_NumWorkGroups.x;
    uint quad_id = gl_LocalInvocationID.x;
    uint vertex_id = gl_LocalInvocationID.y;

    uint dst_i = quad_id * 4 + vertex_id;
    uint src_i = uint(mod(dst_i, 4));

    vec4 pos = initial_pos[src_i];
    pos.xy *= 0.15;

    pos.x += float(quad_id) * 0.4 - 0.7;

    float jump = float(quad_id) + u_time * 4.0;
    jump = cos(jump) * 0.5 + 0.5;
    jump = pow(jump + 0.1, 16.0);
    jump *= 0.06;
    jump -= 0.12;
    pos.y += jump;

    vertices[dst_i].in_pos = pos;

    vec4 uv = initial_uv[src_i];
    vertices[dst_i].in_uv = uv;

    vec3 RGB = vec3(44.74, 0.77, 2.43);
    vertices[dst_i].in_color = vec4(RGB, 1.0);
    vertices[dst_i].in_color.w = 1.0;
}
