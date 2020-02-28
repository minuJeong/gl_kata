#version 460

layout(triangles) in;
layout(triangle_strip, max_vertices=3) out;

in VS_OUT
{
    vec4 vs_local_pos;
    vec4 vs_world_pos;
} vs_out[];

out GS_OUT
{
    vec4 gs_local_pos;
    vec4 gs_world_pos;
    vec4 gs_normal;
} gs_out;

uniform float u_time;
uniform mat4 vp = mat4(1.0);


highp float hash13(vec3 n)
{
    highp vec3 p = vec3(12.532143, 3.431567, 77.432162);
    highp float x = dot(p, n);
    x = mod(x, 3.14159284 * 2.0);
    x = fract(cos(x) * 43215.532143);
    return x;
}

void main()
{
    vec3 a = (vs_out[1].vs_world_pos - vs_out[0].vs_world_pos).xyz;
    vec3 b = (vs_out[2].vs_world_pos - vs_out[0].vs_world_pos).xyz;
    vec3 normal = normalize(cross(b, a));

    float offset_progress = cos(u_time * 8.0) * 0.45 + 0.5;
    offset_progress = pow(offset_progress, 6.0) * 0.5;
    offset_progress += hash13(normal) * 0.1;
    vec3 offset = offset_progress * normal;

    for (int i = 0; i < gl_in.length(); i++)
    {
        vec4 pos = vs_out[i].vs_world_pos;
        pos += vec4(offset, 0.0);
        gl_Position = vp * pos;

        gs_out.gs_normal = vec4(normal, 1.0);
        gs_out.gs_local_pos = vs_out[i].vs_local_pos;
        gs_out.gs_world_pos = vs_out[i].vs_world_pos;
        EmitVertex();
    }
    EndPrimitive();
}
