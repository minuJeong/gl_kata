#version 460

in vec2 in_position;
out vec2 vs_position;

void main()
{
    vs_position = in_position;
    gl_Position = vec4(vs_position.xy, 0.0, 1.0);
}
