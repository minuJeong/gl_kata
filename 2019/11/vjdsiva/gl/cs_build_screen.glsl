#version 460
layout(local_size_x=1) in;

layout(binding=0) buffer vbo
{
    vec2 pos[];
};

layout(binding=1) buffer ibo
{
    int index[];
};

void main()
{
    pos[0] = vec2(-1.0, -1.0);
    pos[1] = vec2(-1.0, +1.0);
    pos[2] = vec2(+1.0, -1.0);
    pos[3] = vec2(+1.0, +1.0);

    index[0] = 0;
    index[1] = 1;
    index[2] = 2;
    index[3] = 2;
    index[4] = 1;
    index[5] = 3;
}
