#version 460

in vec3 ls_pos;
in vec3 ws_pos;
in vec3 vs_pos_0;
in vec4 vs_pos_1;
in vec4 vs_pos_2;
in vec4 vs_pos_3;
in vec2 vs_pos_4;
in vec4 vs_pos_5;
in vec4 vs_pos_6;
in vec4 vs_texcoord_0;
in vec4 vs_texcoord_1;
in vec4 vs_texcoord_2;
in vec4 vs_texcoord_3;
in vec4 vs_texcoord_4;
in vec4 vs_texcoord_5;
in vec4 vs_texcoord_6;
in vec4 vs_texcoord_7;
in vec3 vs_computed_normal;

out vec4 fs_color;

void main()
{
    vec3 N = vs_computed_normal;
    vec3 L = normalize(vec3(20.0, 70.0, 50.0) - ws_pos);

    float lambert = dot(N, L);
    lambert = max(lambert, 0.1);

    fs_color = vec4(lambert, lambert, lambert, 1.0);
}
