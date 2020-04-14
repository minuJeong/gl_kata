#version 460

in vec4 in_pos;
out vec4 vs_pos;

uniform mat4 u_view;
uniform mat4 u_perspective;
uniform float u_time;

float hash12(vec2 uv) { return fract(cos(dot(uv, vec2(12.43214, 46.432165)) * 43125.5231432)); }

void main()
{
    vs_pos = in_pos;
    float y = hash12(vs_pos.xz);
    vs_pos.y += y * 0.6 * cos(u_time * 2.0);
    gl_Position = u_perspective * u_view * vs_pos;
}
