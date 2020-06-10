#version 460

in struct GS_OUT
{
    vec4 position;
    vec4 texcoord0;
    vec4 texcoord1;
    float rand;

    vec4 velocity;
} gs_out;
out vec4 fs_color;

void main()
{
    vec2 uv = gs_out.texcoord0.xy * 0.5 + 0.5;
    vec3 rgb = vec3(0.0);
    float alpha = length(gs_out.texcoord1) - 0.5;
    alpha = 1.0 - alpha;

    rgb = vec3(0.2, 0.4, 0.5);
    rgb = gs_out.velocity.xyz * 0.02;
    rgb = normalize(rgb);
    // rgb = gs_out.position.xyz;

    fs_color = vec4(rgb, alpha);
}
