
struct Vertex
{
    vec4 position;
    vec4 normal;
    vec4 texcoord;
};

struct Triangle
{
    int v0;
    int v1;
    int v2;
};

layout(std430, binding=0) buffer vbo
{
    Vertex vbo_vertex[];
};

layout(std430, binding=1) buffer ibo
{
    Triangle ibo_tris[];
};
