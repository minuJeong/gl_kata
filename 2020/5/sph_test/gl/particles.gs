#version 460

layout(points) in;
layout(triangle_strip, max_vertices=4) out;

in struct VS_OUT
{
    vec4 position;
    vec4 texcoord0;
    float rand;

    vec4 velocity;
} vs_out[];

out struct GS_OUT
{
    vec4 position;
    vec4 texcoord0;
    vec4 texcoord1;
    float rand;

    vec4 velocity;
} gs_out;

uniform mat4 u_mvp;
uniform vec2 u_resolution;

void main()
{
    vec3 uvw = vec3(0.0);
    float aspect = u_resolution.y / u_resolution.x;
    vec3 quad_scale = vec3(0.32) * vec3(aspect, 1.0, 1.0);

    gs_out.position = vs_out[0].position;
    gs_out.texcoord0 = vs_out[0].texcoord0;
    gs_out.rand = vs_out[0].rand;
    gs_out.velocity = vs_out[0].velocity;

    vec4 position = u_mvp * vs_out[0].position;

    uvw = vec3(-1.0, -1.0, -1.0);
    gs_out.texcoord1 = vec4(uvw, 1.0);
    gl_Position = position + (vec4(uvw * quad_scale, 0.0));
    EmitVertex();

    uvw = vec3(+1.0, -1.0, -1.0);
    gs_out.texcoord1 = vec4(uvw, 1.0);
    gl_Position = position + (vec4(uvw * quad_scale, 0.0));
    EmitVertex();

    uvw = vec3(-1.0, +1.0, -1.0);
    gs_out.texcoord1 = vec4(uvw, 1.0);
    gl_Position = position + (vec4(uvw * quad_scale, 0.0));
    EmitVertex();

    uvw = vec3(+1.0, +1.0, -1.0);
    gs_out.texcoord1 = vec4(uvw, 1.0);
    gl_Position = position + (vec4(uvw * quad_scale, 0.0));
    EmitVertex();

    EndPrimitive();
}
