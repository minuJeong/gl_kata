#version 460

layout(local_size_x=1) in;

struct Vertex
{
    vec4 pos;
    vec4 normal;
};

struct Tri
{
    int v0;
    int v1;
    int v2;
};

layout(binding=0) buffer vb
{
    Vertex vertices[];
};

layout(binding=1) buffer ib
{
    Tri tris[];
};

uniform float u_time;

void main()
{
    vertices[0].pos.x = cos(u_time * 6.0) * 0.5 - 1.0;
    vertices[0].pos.z = sin(u_time * 6.0) * 0.5 - 1.0;

    vec4 e0 = vertices[tris[0].v0].pos - vertices[tris[0].v1].pos;
    vec4 e1 = vertices[tris[0].v0].pos - vertices[tris[0].v2].pos;
    vec3 normal = cross(e0.xyz, e1.xyz);
    vertices[0].normal.xyz = normalize(normal);
}
