#version 460

flat in uint vs_index;
smooth in vec3 vs_pos;
smooth in vec3 vs_normal;

out vec4 frag_color;

void main()
{
    float r = float(vs_index) / 8.0;
    frag_color = vec4(r, 1.0, 0.5, 1.0);
}
