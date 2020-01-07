#version 460

// 11 tris per thread group, 3 indices per tris
layout(local_size_x=32) in;

struct Triangle
{
    int tri_id;
    int v0;
    int v1;
    int v2;
};

// vertex position buffer
layout(binding=4) buffer vbo
{
    vec4 pos[];
};

// index buffer
layout(binding=5) buffer ibo
{
    Triangle index[];
};

// vertex normal buffer
layout(binding=6) buffer nbo
{
    vec4 normal[];
};

uniform int u_tris_count = 0;

// WIP
vec3 get_abutting_tris_normal(int vertex_idx)
{
    for (int i = 0; i < vertex_idx; i++)
    {
        vec4 v;
    }

    return vec3(0.0);
}

void main()
{
    int face_id = int(gl_LocalInvocationID.x + gl_WorkGroupID.x * 32);

    int vertex_id_0 = index[face_id].v0;
    int vertex_id_1 = index[face_id].v1;
    int vertex_id_2 = index[face_id].v2;

    vec3 v0 = pos[vertex_id_0].xyz;
    vec3 v1 = pos[vertex_id_1].xyz;
    vec3 v2 = pos[vertex_id_2].xyz;

    // WIP
    // vec3 normal_0 = get_abutting_tris_normal(vertex_id_0);
    // vec3 normal_1 = get_abutting_tris_normal(vertex_id_1);
    // vec3 normal_2 = get_abutting_tris_normal(vertex_id_2);

    normal[vertex_id_0] = vec4(normalize(cross(v2 - v0, v1 - v0)), 0.0);
    normal[vertex_id_1] = vec4(normalize(cross(v2 - v1, v0 - v1)), 0.0);
    normal[vertex_id_2] = vec4(normalize(cross(v0 - v2, v1 - v2)), 0.0);
}
