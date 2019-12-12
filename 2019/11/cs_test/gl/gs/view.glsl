#version 460

layout(points) in;
layout(triangle_strip, max_vertices=4) out;

in VS_OUT
{
    vec4 position;
    vec4 velocity;
    vec4 color;
} vs_out[];

out GS_OUT
{
    vec4 position;
    vec4 velocity;
    vec4 color;
    vec4 texcoord;
} gs_out;

void main()
{
    vec4 vs_pos = vs_out[0].position;
    vec4 vs_vel = vs_out[0].velocity;
    vec4 vs_col = vs_out[0].color;

    float scale = 0.06;

    gs_out.velocity = vs_vel;
    gs_out.color = vs_col;

    gs_out.position = vs_pos;
    gs_out.texcoord = vec4(0.0, 0.0, 0.0, 1.0);
    gl_Position = vs_pos + vec4(-1.0, -1.0, 0.0, 0.0) * scale;
    EmitVertex();

    gs_out.position = vs_pos;
    gs_out.texcoord = vec4(1.0, 0.0, 0.0, 1.0);
    gl_Position = vs_pos + vec4(+1.0, -1.0, 0.0, 0.0) * scale;
    EmitVertex();

    gs_out.position = vs_pos;
    gs_out.texcoord = vec4(0.0, 1.0, 0.0, 1.0);
    gl_Position = vs_pos + vec4(-1.0, +1.0, 0.0, 0.0) * scale;
    EmitVertex();

    gs_out.position = vs_pos;
    gs_out.texcoord = vec4(1.0, 1.0, 0.0, 1.0);
    gl_Position = vs_pos + vec4(+1.0, +1.0, 0.0, 0.0) * scale;
    EmitVertex();

    EndPrimitive();
}
