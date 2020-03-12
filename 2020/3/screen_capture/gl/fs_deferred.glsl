#version 460

in vec4 vs_pos;
out vec4 fs_color;

uniform vec2 u_res;
uniform float u_aspect;
uniform float u_time;
uniform float u_ispress_0;
uniform float u_ispress_1;
uniform float u_ispress_2;
uniform sampler2D u_screen_tex;
uniform vec2 u_mousepos;

layout(binding=1) uniform sampler2D u_gbuffer_colour;

void main()
{
    vec2 uv = vs_pos.xy * 0.5 + 0.5;
    vec2 xy = uv.xy * u_res.xy;
    xy.y = u_res.y - xy.y;

    vec3 rgb = texture(u_gbuffer_colour, uv).xyz;

    if (u_ispress_0 > 0.5)
    {
        vec2 dist = u_mousepos - xy;
        float x = 500.0 - length(dist);
        x = max(x, 0.0);
        x /= 500.0;
        x = pow(x + 0.05, 5.0);
        rgb *= 1.0 + x;
    }

    float alpha = 1.0 - u_ispress_1;
    fs_color = vec4(rgb * alpha, alpha);
}
