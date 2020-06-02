#version 460

layout(points) in;
layout(triangle_strip, max_vertices=4) out;

in struct VS_OUT
{
    vec4 position;
    vec2 texcoord0;
    float rand;
} vs_out[];

out struct GS_OUT
{
    vec4 position;
    vec2 texcoord0;
    vec2 texcoord1;
    float rand;
} gs_out;

void main()
{
    vec2 uv = vec2(0.0);
    float quad_scale = 0.00002;

    gs_out.position = vs_out[0].position;
    gs_out.texcoord0 = vs_out[0].texcoord0;
    gs_out.rand = vs_out[0].rand;

    uv = vec2(-1.0, -1.0);
    gs_out.texcoord1 = uv;
    gl_Position = gs_out.position + (vec4(uv * quad_scale, 0.0, 0.0));
    EmitVertex();

    uv = vec2(+1.0, -1.0);
    gs_out.texcoord1 = uv;
    gl_Position = gs_out.position + (vec4(uv * quad_scale, 0.0, 0.0));
    EmitVertex();

    uv = vec2(-1.0, +1.0);
    gs_out.texcoord1 = uv;
    gl_Position = gs_out.position + (vec4(uv * quad_scale, 0.0, 0.0));
    EmitVertex();

    uv = vec2(+1.0, +1.0);
    gs_out.texcoord1 = uv;
    gl_Position = gs_out.position + (vec4(uv * quad_scale, 0.0, 0.0));
    EmitVertex();

    EndPrimitive();
}
