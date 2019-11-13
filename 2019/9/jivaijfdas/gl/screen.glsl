#version 460

layout(local_size_x=1) in;
layout(binding=0) buffer vbo
{
    vec4 vertices[];
};

layout(binding=1) buffer ibo
{
    int indices[];
};

void main()
{
    int i = 0;
    for (float x = 0.0; x < 2.0; x += 1.0)
    {
        for (float y = 0.0; y < 2.0; y += 1.0)
        {
            vertices[i] = vec4(x * 2.0 - 1.0, y * 2.0 - 1.0, x, y);
            i++;
        }
    }

    indices[0] = 0;
    indices[1] = 1;
    indices[2] = 2;
    indices[3] = 2;
    indices[4] = 1;
    indices[5] = 3;
}
