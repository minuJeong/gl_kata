#version 460


layout(location=0) uniform sampler2D u_tex;

in vec2 _uv;
out vec4 out_color;


float lum(vec4 col)
{
    return 0.21 * col.x + 0.71 * col.y + 0.08 * col.z;
}

void main()
{
    const float u_width = 512;

    float pixel_size = 1.0 / u_width;
    vec2 xy = _uv * u_width;

    vec4 window[25];
    for (float x = -2.0; x <= 2.0; x++)
    {
        for (float y = -2.0; y <= 2.0; y++)
        {
            vec2 offset = vec2(x, y) * pixel_size;
            vec2 oxy = xy + vec2(x, y);

            int i = int(oxy.x + oxy.y * u_width);
            window[i] = texture(u_tex, _uv + offset);
        }
    }

    for (int i = 25 - 1; i > 0; i--)
    {
        vec4 a = window[i];
        vec4 b = window[i - 1];

        if (lum(a) < lum(b))
        {
            window[i] = b;
            window[i - 1] = a;
        }
    }

    vec4 median = window[12];

    out_color = vec4(median.xyz, 1.0);
}
