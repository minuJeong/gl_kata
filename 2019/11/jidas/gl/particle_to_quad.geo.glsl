#version 460

layout(points) in;
layout(triangle_strip, max_vertices=4) out;

in vec4 vs_pos[];
in vec4 vs_vel[];

out vec4 gs_pos;
out vec4 gs_vel;
out vec2 gs_uv;


void emit_quad(vec4 pos)
{
    pos.w = 1.0;

    const float SIZE = 0.004;

    vec4 emit_pos;

    gs_uv = vec2(-1.0, -1.0);
    emit_pos = pos + vec4(gs_uv * SIZE, 0.0, 0.0);
    gs_pos = emit_pos;
    gl_Position = emit_pos;
    EmitVertex();

    gs_uv = vec2(+1.0, -1.0);
    emit_pos = pos + vec4(gs_uv * SIZE, 0.0, 0.0);
    gs_pos = emit_pos;
    gl_Position = emit_pos;
    EmitVertex();

    gs_uv = vec2(-1.0, +1.0);
    emit_pos = pos + vec4(gs_uv * SIZE, 0.0, 0.0);
    gs_pos = emit_pos;
    gl_Position = emit_pos;
    EmitVertex();

    gs_uv = vec2(+1.0, +1.0);
    emit_pos = pos + vec4(gs_uv * SIZE, 0.0, 0.0);
    gs_pos = emit_pos;
    gl_Position = emit_pos;
    EmitVertex();

    EndPrimitive();
}

void main()
{
    vec4 pos = gl_in[0].gl_Position;
    emit_quad(pos);
}
