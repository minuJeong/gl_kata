#version 460

struct Particle
{
    vec4 position;
    vec4 velocity;
    vec4 color;
};

layout(binding=0) buffer vbo
{
    Particle particles[];
};

in vec2 vs_pos;
out vec4 fs_color;

void main()
{
    vec3 RGB = vec3(0.12 - vs_pos.y * 0.08);
    fs_color = vec4(RGB, 1.0);
}
