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

void main()
{
    float x = -1.0, y = -1.0, z = -1.0, w = 1.0;

    vec4 p = vec4(x, y, z, w);

    Vertex V;
    // 0: ---
    V.pos = vec4(-1.0, -1.0, -1.0, 1.0);
    V.normal = vec4(normalize(V.pos.xyz), 1.0);
    vertices[0] = V;

    // 1: +--
    V.pos = vec4(+1.0, -1.0, -1.0, 1.0);
    V.normal = vec4(normalize(V.pos.xyz), 1.0);
    vertices[1] = V;

    // 2: -+-
    V.pos = vec4(-1.0, +1.0, -1.0, 1.0);
    V.normal = vec4(normalize(V.pos.xyz), 1.0);
    vertices[2] = V;

    // 3: ++-
    V.pos = vec4(+1.0, +1.0, -1.0, 1.0);
    V.normal = vec4(normalize(V.pos.xyz), 1.0);
    vertices[3] = V;

    // 4: +++
    V.pos = vec4(-1.0, -1.0, +1.0, 1.0);
    V.normal = vec4(normalize(V.pos.xyz), 1.0);
    vertices[4] = V;

    V.pos = vec4(+1.0, -1.0, +1.0, 1.0);
    V.normal = vec4(normalize(V.pos.xyz), 1.0);
    vertices[5] = V;

    V.pos = vec4(-1.0, +1.0, +1.0, 1.0);
    V.normal = vec4(normalize(V.pos.xyz), 1.0);
    vertices[6] = V;

    V.pos = vec4(+1.0, +1.0, +1.0, 1.0);
    V.normal = vec4(normalize(V.pos.xyz), 1.0);
    vertices[7] = V;

    Tri t;
    t.v0 = 0;
    t.v1 = 1;
    t.v2 = 2;
    tris[0] = t;

    t.v0 = 2;
    t.v1 = 1;
    t.v2 = 3;
    tris[1] = t;


    t.v0 = 4;
    t.v1 = 5;
    t.v2 = 6;
    tris[2] = t;

    t.v0 = 6;
    t.v1 = 5;
    t.v2 = 7;
    tris[3] = t;


    t.v0 = 5;
    t.v1 = 1;
    t.v2 = 7;
    tris[4] = t;

    t.v0 = 7;
    t.v1 = 1;
    t.v2 = 3;
    tris[5] = t;


    t.v0 = 0;
    t.v1 = 4;
    t.v2 = 2;
    tris[6] = t;

    t.v0 = 2;
    t.v1 = 4;
    t.v2 = 6;
    tris[7] = t;


    t.v0 = 0;
    t.v1 = 4;
    t.v2 = 1;
    tris[8] = t;

    t.v0 = 1;
    t.v1 = 4;
    t.v2 = 5;
    tris[9] = t;


    t.v0 = 2;
    t.v1 = 3;
    t.v2 = 6;
    tris[10] = t;

    t.v0 = 6;
    t.v1 = 3;
    t.v2 = 7;
    tris[11] = t;
}
