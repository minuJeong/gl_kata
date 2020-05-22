#version 460

layout(points) in;
layout(triangle_strip, max_vertices=8) out;

in VSOUT
{
    vec4 pos;
} gs_in[];
out GSOUT
{
    vec4 pos;
} gs_out;

uniform mat4 u_mvp;
uniform float u_time;

float hash12(vec2 uv)
{
    return fract(cos(dot(uv, vec2(12.325, 43.423)) * 2345.4321) * 43125.4321);
}

void main()
{
    // (^2) / 2
    const float XZ_SIZE = 0.0707;
    mat4 mvp = u_mvp;

    vec4 p = gl_in[0].gl_Position;
    float rotation = u_time * hash12(p.xz) * 4.0;
    float c = cos(rotation), s = sin(rotation);

    for (float x = -1.0; x < 2.0; x += 2.0)
    for (float z = -1.0; z < 2.0; z += 2.0)
    {
        // float y = hash12(p.xz) * 0.2;
        vec4 offset = vec4(XZ_SIZE * x, 0.0, XZ_SIZE * z, 0.0);

        vec4 pos = p + offset;
        gs_out.pos.xyzw = pos.xyzw;

        offset.xz = mat2(c, -s, s, c) * offset.xz;
        gl_Position = mvp * (p + offset);
        EmitVertex();
    }

    EndPrimitive();
}
