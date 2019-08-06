
#version 460

layout(local_size_x=8, local_size_y=8, local_size_z=8) in;
layout(binding=0) buffer out_buffer
{
    vec4 out_col[];
};

uniform uint u_width;
uniform uint u_height;
uniform uint u_depth;
uniform uint u_z_hor;
uniform uint u_z_ver;

float sdf_sphere(vec3 p, float r)
{
    return length(p) - r;
}


uint i_at(uvec3 xyz)
{
    float Z = float(xyz.z);
    float x_offset = mod(Z, u_z_hor) * u_width;
    float y_offset = floor(Z / u_z_hor) * u_height;

    uint wxh = u_width * u_z_hor;
    uint i = uint(xyz.x + x_offset + (xyz.y + y_offset) * wxh);
    return i;
}

vec3 get_uvw(uvec3 xyz)
{
    vec3 whd = vec3(u_width, u_height, u_depth);
    return xyz / whd;
}


void main()
{
    uvec3 xyz = gl_LocalInvocationID.xyz + gl_WorkGroupID.xyz * uvec3(8, 8, 8);

    uint i = i_at(xyz);
    vec3 uvw = get_uvw(xyz);

    vec3 cuvw = uvw * 2.0 - 1.0;
    float distance = sdf_sphere(cuvw, 0.9);
    
    float inner_edge = smoothstep(-0.01, 0.0, distance);
    float outter_edge = smoothstep(0.0, -0.01, distance);
    float edge = inner_edge * outter_edge;

    out_col[i] = vec4(edge, edge, edge, 1.0);
}
