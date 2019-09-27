#version 460

layout(local_size_x=8) in;
layout(binding=0) buffer vbo
{
    vec3 pos[];
};

layout(binding=1) buffer nbo
{
    vec3 normal[];
};

layout(binding=2) buffer ibo
{
    int index[];
};

uniform float u_time;

    
mat3 look_at(vec3 origin, vec3 target)
{
    vec3 UP = vec3(0.0, 1.0, 0.0);
    vec3 forward = normalize(target - origin);
    vec3 right = normalize(cross(forward, UP));
    vec3 local_up = normalize(cross(right, forward));

    return mat3(right, local_up, forward);
}

void main()
{
    vec3 o = vec3(0.0);
    
    mat3 top    = look_at(o, vec3(0.0, 0.0, +1.0));
    mat3 bottom = look_at(o, vec3(0.0, 0.0, -1.0));
    mat3 left   = look_at(o, vec3(-1.0, 0.0, 0.0));
    mat3 right  = look_at(o, vec3(+1.0, 0.0, 0.0));
    mat3 front  = look_at(o, vec3(0.0, +1.0, 0.0));
    mat3 back   = look_at(o, vec3(0.0, -1.0, 0.0));

    vec3 leftup = vec3(-1.0, -1.0, 0.0);
    vec3 rightup = vec3(+1.0, -1.0, 0.0);
    vec3 leftdown = vec3(-1.0, +1.0, 0.0);
    vec3 rightdown = vec3(+1.0, +1.0, 0.0);

    pos[0] = top * leftup;
    pos[1] = top * rightup;
    pos[2] = top * leftdown;
    pos[3] = top * rightdown;

    pos[4] = bottom * leftup;
    pos[5] = bottom * rightup;
    pos[6] = bottom * leftdown;
    pos[7] = bottom * rightdown;

    for (int i = 0; i < 6; i++)
    {
        index[i * 6 + 0] = i * 6 + 0;
        index[i * 6 + 1] = i * 6 + 1;
        index[i * 6 + 2] = i * 6 + 2;
        index[i * 6 + 3] = i * 6 + 2;
        index[i * 6 + 4] = i * 6 + 1;
        index[i * 6 + 5] = i * 6 + 3;
    }
}
