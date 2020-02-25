#version 460

layout(local_size_x=1) in;

struct Vertex
{
    vec4 pos;
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

void main()
{}
