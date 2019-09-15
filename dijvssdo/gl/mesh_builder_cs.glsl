#version 460

layout(local_size_x=1) in;

layout(binding=0) buffer vbo_bind
{
    vec2 vertices[];
};

layout(binding=1) buffer ibo_bind
{
    int indices[];
};

void main()
{
    vertices[0] = vec2(-1.0, -1.0);
    vertices[1] = vec2(+1.0, -1.0);
    vertices[2] = vec2(-1.0, +1.0);
    vertices[3] = vec2(+1.0, +1.0);
    
    indices[0] = 0;
    indices[1] = 1;
    indices[2] = 2;
    indices[3] = 2;
    indices[4] = 1;
    indices[5] = 3;
}
