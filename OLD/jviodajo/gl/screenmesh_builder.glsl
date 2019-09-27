#version 460

layout(local_size_x=1) in;

layout(binding=0) buffer vbo
{
    vec4 vertices[];
};

layout(binding=1) buffer ibo
{
    int indices[6];
};

void main()
{
    vertices[0] = vec4(-1.0, -1.0, 0.0, 0.0);
    vertices[1] = vec4(+1.0, -1.0, 1.0, 0.0);
    vertices[2] = vec4(-1.0, +1.0, 0.0, 1.0);
    vertices[3] = vec4(+1.0, +1.0, 1.0, 1.0);

    indices = int[](0, 1, 2, 2, 1, 3);
}
