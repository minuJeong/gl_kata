#version 460
#include ./gl/cs/_struct.glsl

layout(local_size_x=2, local_size_y=2, local_size_z=2) in;

uniform float u_time;

float random(vec3 p)
{
    return fract(sin(dot(p, vec3(43666.234, 11999.342, 566.4333))) * 4325543.54321);
}

void main()
{
    uvec3 ID = gl_LocalInvocationID.xyz;

    // xyz = vec3(+0.0 ~ +1.0)
    vec3 xyz = vec3(ID.xyz);

    // xyz = vec3(-1.0 ~ +1.0)
    xyz = xyz * 2.0 - 1.0;

    xyz.x += cos(u_time * 10.0) * sin(u_time * 10.0);

    Vertex vertex;
    vertex.position = vec4(xyz, 1.0);
    vertex.normal = vec4(0.0, 0.0, 0.0, 1.0);
    vertex.texcoord = vec4(0.0, 0.0, 0.0, 1.0);

    uint i = ID.x + ID.y * 2 + ID.z * 4;
    vbo_vertex[i] = vertex;
}
