#version 460

layout(local_size_x=1) in;

struct Vertex
{
    vec4 pos;
    vec4 normal;
};

struct Quad
{
    int v00;
    int v01;
    int v02;

    int v10;
    int v11;
    int v12;
};

layout(binding=0) buffer vb
{
    Vertex vertices[];
};

layout(binding=1) buffer ib
{
    Quad quads[];
};

void main()
{
    int i = 0;
    Vertex V;
    for (float z = -1.0; z <= 1.0; z+= 2)
    {
        for (float y = -1.0; y <= 1.0; y+= 2)
        {
            for (float x = -1.0; x <= 1.0; x+= 2)
            {
                V.pos = vec4(x, y, z, 1.0);
                vertices[i++] = V;
            }
        }
    }

    Quad q;
    q.v00 = 0;
    q.v01 = 2;
    q.v02 = 1;
    q.v10 = 1;
    q.v11 = 2;
    q.v12 = 3;
    quads[0] = q;

    q.v00 = 5;
    q.v01 = 7;
    q.v02 = 6;
    q.v10 = 4;
    q.v11 = 5;
    q.v12 = 6;
    quads[1] = q;

    q.v00 = 5;
    q.v01 = 1;
    q.v02 = 7;
    q.v10 = 1;
    q.v11 = 3;
    q.v12 = 7;
    quads[2] = q;

    q.v00 = 0;
    q.v01 = 4;
    q.v02 = 2;
    q.v10 = 2;
    q.v11 = 4;
    q.v12 = 6;
    quads[3] = q;

    q.v00 = 0;
    q.v01 = 1;
    q.v02 = 4;
    q.v10 = 4;
    q.v11 = 1;
    q.v12 = 5;
    quads[4] = q;

    q.v00 = 2;
    q.v01 = 6;
    q.v02 = 3;
    q.v10 = 3;
    q.v11 = 6;
    q.v12 = 7;
    quads[5] = q;
}
