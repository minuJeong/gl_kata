#version 460

layout(local_size_x=1) in;

layout(binding=2) buffer constants
{
    float u_aspect;
    float u_time;
};

layout(binding=0) buffer vb
{
    vec4 vertices[4];
};

void main()
{
    float spd = 1.0;
    float plusone = 1.0;
    float minone = -1.0;

    float c = cos(u_time), s = sin(u_time);
    mat2 rotation = mat2(c, -s, s, c);
    rotation = mat2(1.0, 0.0, 0.0, 1.0);

    vertices[0] = vec4(rotation * vec2(minone, minone), 0.0, 1.0);
    vertices[1] = vec4(rotation * vec2(plusone, minone), 0.0, 1.0);
    vertices[2] = vec4(rotation * vec2(minone, plusone), 0.0, 1.0);
    vertices[3] = vec4(rotation * vec2(plusone, plusone), 0.0, 1.0);
}
