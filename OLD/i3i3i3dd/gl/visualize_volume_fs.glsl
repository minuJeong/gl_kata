#version 460

layout(binding=0) buffer v0
{
    float density[];
};

in vec2 vs_pos;
out vec4 fs_color;

uniform ivec2 u_res;

void main()
{
    fs_color = vec4(vs_pos * 0.5 + 0.5, u_res.x, 1.0);
}
