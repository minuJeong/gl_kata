#version 460

in vec2 vs_uv;
in vec2 vs_pos;
out vec4 fs_color;

layout(binding=3) uniform sampler2D tex_realsense_color;
layout(binding=4) uniform sampler2D tex_realsense_depth;

uniform vec2 u_rs_color_resolution;
uniform vec2 u_rs_depth_resolution;
uniform vec2 u_screen_resolution;

uniform float u_time;


float color_aspect()
{
    return u_rs_color_resolution.x / u_rs_color_resolution.y;
}

float depth_aspect()
{
    return u_rs_depth_resolution.x / u_rs_depth_resolution.y;
}

void main()
{
    float screen_aspect = u_screen_resolution.x / u_screen_resolution.y;

    vec2 uv = vs_uv;
    uv.x *= screen_aspect;
    uv = 1.0 - uv;

    vec2 color_uv = uv;
    color_uv.x /= color_aspect();
    vec3 color = texture(tex_realsense_color, uv).xyz;

    vec2 depth_uv = uv;
    // depth_uv.x /= depth_aspect();
    float depth = texture(tex_realsense_depth, depth_uv).x * 5000.0;
    depth = min(max(depth, 0.0), 1.0);

    vec3 RGB = mix(depth.xxx, color, cos(u_time * 4.0) * 0.5 + 0.5);
    fs_color = vec4(RGB, 1.0);
}
