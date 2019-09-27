#version 460

layout(local_size_x=1) in;

struct Vertex
{
    vec2 pos;
    vec2 uv;
};

layout(binding=0) buffer vbo
{
    Vertex vertices[];
};

layout(binding=1) buffer ibo
{
    int indices[];
};

void main()
{
    vertices[0] = Vertex(vec2(-1.0, -1.0), vec2(0.0, 0.0));
    vertices[1] = Vertex(vec2(+1.0, -1.0), vec2(1.0, 0.0));
    vertices[2] = Vertex(vec2(-1.0, +1.0), vec2(0.0, 1.0));
    vertices[3] = Vertex(vec2(+1.0, +1.0), vec2(1.0, 1.0));

    indices[0] = 0;
    indices[1] = 1;
    indices[2] = 2;
    indices[3] = 2;
    indices[4] = 1;
    indices[5] = 3;
}
